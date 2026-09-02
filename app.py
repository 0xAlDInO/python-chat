import eventlet
eventlet.monkey_patch()

import os
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from flask_socketio import SocketIO, join_room, emit
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure Upload Folder
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max limit

# Configure Database URI (MySQL with SQLite fallback if MYSQL_HOST is not set)
db_user = os.getenv('MYSQL_USER', 'root')
db_password = os.getenv('MYSQL_PASSWORD', '')
db_host = os.getenv('MYSQL_HOST', 'localhost')
db_name = os.getenv('MYSQL_DATABASE', 'oxmember_db')

mysql_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
sqlite_fallback_uri = "sqlite:///oxmember.db"

default_db_uri = mysql_uri if os.getenv('MYSQL_HOST') else sqlite_fallback_uri
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', default_db_uri)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)

# Active calls state in memory: { call_id: { 'call_id': id, 'room': room, 'host': host, 'type': 'video'|'audio', 'participants': [user1, user2] } }
active_calls = {}

# Database Models
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    room = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    file_url = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.String(20), nullable=True) # 'image' or 'file'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'room': self.room,
            'message': self.message,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'timestamp': self.timestamp.strftime('%H:%M')
        }

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/socket.io.js')
def socketio_js():
    return app.send_static_file('socket.io.js')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(f"{int(datetime.utcnow().timestamp())}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        file_url = f"/static/uploads/{filename}"

        # Determine file type
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        file_type = 'image' if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'] else 'file'

        return jsonify({
            'file_url': file_url,
            'filename': file.filename,
            'file_type': file_type
        })

@app.route('/api/history/<room>')
def get_room_history(room):
    messages = Message.query.filter_by(room=str(room)).order_by(Message.timestamp.asc()).all()
    return jsonify([msg.to_dict() for msg in messages])

def get_room_calls(room):
    return [c for c in active_calls.values() if str(c['room']) == str(room)]

def broadcast_room_calls(room):
    calls = get_room_calls(room)
    socketio.emit('active_calls_update', calls, room=str(room))

@socketio.on('envoie_message')
def handle_send_message_event(data):
    app.logger.info(f"{data['username']} a envoyé un message au room {data['room']}: {data['message']}")

    # Persist message in DB
    new_msg = Message(
        username=data['username'],
        room=str(data['room']),
        message=data.get('message', ''),
        file_url=data.get('file_url'),
        file_type=data.get('file_type')
    )
    db.session.add(new_msg)
    db.session.commit()

    msg_dict = new_msg.to_dict()
    socketio.emit('recu_msg', msg_dict, room=data['room'])

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info(f"{data['username']} a rejoint le room {data['room']}")
    join_room(data['room'])
    socketio.emit('announcement_join_room', data, room=data['room'])
    # Send current active calls in room to joining user
    emit('active_calls_update', get_room_calls(data['room']))

# Call Queue & Multi-Party WebRTC Signaling Handlers
@socketio.on('create_call')
def handle_create_call(data):
    room = str(data['room'])
    caller = data['username']
    call_type = data.get('call_type', 'video') # 'video' or 'audio'
    call_id = f"call_{int(time.time()*1000)}"

    type_label = "Vidéo" if call_type == 'video' else "Audio"
    active_calls[call_id] = {
        'call_id': call_id,
        'room': room,
        'host': caller,
        'call_type': call_type,
        'title': f"Appel {type_label} de {caller}",
        'participants': [caller]
    }

    broadcast_room_calls(room)
    emit('call_created', active_calls[call_id])

@socketio.on('join_call')
def handle_join_call(data):
    room = str(data['room'])
    call_id = data['call_id']
    username = data['username']

    if call_id in active_calls:
        if username not in active_calls[call_id]['participants']:
            active_calls[call_id]['participants'].append(username)

        broadcast_room_calls(room)
        # Broadcast to everyone in call that a new user joined so existing peers can initiate WebRTC peer connections
        emit('user_joined_call', {
            'call_id': call_id,
            'joined_user': username,
            'participants': active_calls[call_id]['participants'],
            'call_type': active_calls[call_id]['call_type']
        }, room=room)

@socketio.on('leave_call')
def handle_leave_call(data):
    room = str(data['room'])
    call_id = data['call_id']
    username = data['username']

    if call_id in active_calls:
        if username in active_calls[call_id]['participants']:
            active_calls[call_id]['participants'].remove(username)

        emit('user_left_call', {'call_id': call_id, 'username': username}, room=room)

        # Delete call if empty
        if len(active_calls[call_id]['participants']) == 0:
            del active_calls[call_id]

        broadcast_room_calls(room)

# Targeted WebRTC Peer-to-Peer Signaling
@socketio.on('webrtc_signal')
def handle_webrtc_signal(data):
    # Route signal (offer, answer, candidate) to specific target peer or broadcast to room
    emit('webrtc_signal', data, room=data['room'], include_self=False)

if __name__ == "__main__":
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
