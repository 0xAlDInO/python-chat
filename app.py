import os
try:
    import eventlet
    eventlet.monkey_patch()
except Exception:
    pass
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

# Active calls state in memory
active_calls = {}

# Many-to-Many Association Table for User <-> Room Authorizations
user_rooms = db.Table('user_rooms',
    db.Column('user_id', db.String(50), db.ForeignKey('users.id'), primary_key=True),
    db.Column('room_id', db.String(50), db.ForeignKey('rooms.id'), primary_key=True)
)

# Database Models
class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.String(50), primary_key=True) # e.g. "dev", "reunion", "directeur", "101"
    name = db.Column(db.String(100), nullable=False) # e.g. "Salle Développement"
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(50), primary_key=True) # e.g. "OX-001"
    nom = db.Column(db.String(80), nullable=False)
    prenom = db.Column(db.String(80), nullable=False)
    fonction = db.Column(db.String(100), nullable=False)

    # Relationship to authorized rooms
    authorized_rooms = db.relationship('Room', secondary=user_rooms, lazy='subquery',
        backref=db.backref('users', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'full_name': f"{self.prenom} {self.nom}",
            'fonction': self.fonction,
            'authorized_rooms': [r.to_dict() for r in self.authorized_rooms]
        }

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

# Pre-populate Back-Office database with users, rooms, and authorization relationships
def init_db_data():
    db.create_all()

    # Create Rooms if empty
    if Room.query.count() == 0:
        r_gen = Room(id="101", name="Salon Général", description="Espace général des collaborateurs")
        r_dev = Room(id="dev", name="Salle Développement", description="Équipe technique et ingénierie")
        r_reu = Room(id="reunion", name="Salle Réunion", description="Espace de briefing et réunions")
        r_dir = Room(id="directeur", name="Salle Direction", description="Comité de direction Oxalix")

        db.session.add_all([r_gen, r_dev, r_reu, r_dir])
        db.session.commit()

    # Create Users and Assign Authorized Rooms if empty
    if User.query.count() == 0:
        r_gen = Room.query.get("101")
        r_dev = Room.query.get("dev")
        r_reu = Room.query.get("reunion")
        r_dir = Room.query.get("directeur")

        u1 = User(id="OX-001", prenom="Alice", nom="Dupont", fonction="Chef de Projet")
        u1.authorized_rooms = [r_gen, r_dev, r_reu]

        u2 = User(id="OX-002", prenom="Jean", nom="Martin", fonction="Développeur Senior")
        u2.authorized_rooms = [r_gen, r_dev]

        u3 = User(id="OX-003", prenom="Sophie", nom="Bernard", fonction="UI/UX Designer")
        u3.authorized_rooms = [r_gen, r_reu]

        u4 = User(id="OX-004", prenom="Thomas", nom="Dubois", fonction="Ingénieur DevOps")
        u4.authorized_rooms = [r_gen, r_dev]

        u5 = User(id="OX-005", prenom="Claire", nom="Moreau", fonction="Directrice Générale")
        u5.authorized_rooms = [r_gen, r_dev, r_reu, r_dir]

        db.session.add_all([u1, u2, u3, u4, u5])
        db.session.commit()

with app.app_context():
    init_db_data()

@app.cli.command('init-db')
def init_db_command():
    """Crée les tables et initialise les données utilisateurs/salles par défaut."""
    init_db_data()
    print("Base de données initialisée avec succès ! Les utilisateurs et leurs autorisations :")
    for u in User.query.all():
        rooms_list = ", ".join([f"{r.name} ({r.id})" for r in u.authorized_rooms])
        print(f"  - {u.id}: {u.prenom} {u.nom} ({u.fonction}) -> Salles: [{rooms_list}]")

@app.route('/')
def home():
    error = request.args.get('error')
    return render_template("index.html", error=error)

@app.route('/socket.io.js')
def socketio_js():
    return app.send_static_file('socket.io.js')

@app.route('/api/user/rooms/<user_id>')
def get_user_rooms(user_id):
    user = User.query.filter_by(id=user_id.strip().upper()).first()
    if user:
        return jsonify({
            'valid': True,
            'authorized_rooms': [r.to_dict() for r in user.authorized_rooms]
        })
    return jsonify({'valid': False, 'error': 'ID Utilisateur inexistant'}), 404

@app.route('/chat')
def chat():
    user_id = request.args.get('user_id', '').strip().upper()
    room_id = request.args.get('room', '').strip().lower()

    if not user_id or not room_id:
        return redirect(url_for('home', error="Veuillez renseigner votre ID et la salle de discussion."))

    # 1. Check if user exists
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return redirect(url_for('home', error=f"Identifiant '{user_id}' inexistant dans la base Back-Office."))

    # 2. Check if room exists
    room = Room.query.filter_by(id=room_id).first()
    if not room:
        # Check by name if ID was passed as full name
        room = Room.query.filter(Room.name.ilike(room_id)).first()

    if not room:
        return redirect(url_for('home', error=f"La salle '{room_id}' n'existe pas."))

    # 3. Check authorization: does the user have access to this room?
    if room not in user.authorized_rooms:
        return redirect(url_for('home', error=f"Accès refusé : L'identifiant {user.id} n'a pas l'autorisation pour la {room.name} ({room.id})."))

    return render_template(
        'chat.html',
        user_id=user.id,
        username=f"{user.prenom} {user.nom}",
        fonction=user.fonction,
        room=room.id,
        room_name=room.name,
        user_authorized_rooms=[r.to_dict() for r in user.authorized_rooms]
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if file:
        filename = secure_filename(f"{int(datetime.utcnow().timestamp())}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        file_url = f"/static/uploads/{filename}"

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
    emit('active_calls_update', get_room_calls(data['room']))

# Call Queue & Multi-Party WebRTC Signaling Handlers
@socketio.on('create_call')
def handle_create_call(data):
    room = str(data['room'])
    caller = data['username']
    call_type = data.get('call_type', 'video')
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
        call = active_calls[call_id]

        if username == call['host']:
            emit('call_ended', {'call_id': call_id, 'host': username}, room=room)
            del active_calls[call_id]
        else:
            if username in call['participants']:
                call['participants'].remove(username)
            emit('user_left_call', {'call_id': call_id, 'username': username}, room=room)
            if len(call['participants']) == 0:
                del active_calls[call_id]

        broadcast_room_calls(room)

# Targeted WebRTC Peer-to-Peer Signaling
@socketio.on('webrtc_signal')
def handle_webrtc_signal(data):
    emit('webrtc_signal', data, room=data['room'], include_self=False)

if __name__ == "__main__":
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
