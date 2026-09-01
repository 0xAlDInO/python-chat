import eventlet
eventlet.monkey_patch()

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, join_room, emit
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure Database URI (MySQL with SQLite fallback if MySQL is not configured)
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

# Database Models
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    room = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'room': self.room,
            'message': self.message,
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

@app.route('/api/history/<room>')
def get_room_history(room):
    messages = Message.query.filter_by(room=str(room)).order_by(Message.timestamp.asc()).all()
    return jsonify([msg.to_dict() for msg in messages])

@socketio.on('envoie_message')
def handle_send_message_event(data):
    app.logger.info(f"{data['username']} a envoyé un message au room {data['room']}: {data['message']}")

    # Persist message in DB
    new_msg = Message(
        username=data['username'],
        room=str(data['room']),
        message=data['message']
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

@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    emit('webrtc_offer', data, room=data['room'], include_self=False)

@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    emit('webrtc_answer', data, room=data['room'], include_self=False)

@socketio.on('webrtc_ice_candidate')
def handle_webrtc_ice_candidate(data):
    emit('webrtc_ice_candidate', data, room=data['room'], include_self=False)

@socketio.on('webrtc_end_call')
def handle_webrtc_end_call(data):
    emit('webrtc_end_call', data, room=data['room'], include_self=False)

if __name__ == "__main__":
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
