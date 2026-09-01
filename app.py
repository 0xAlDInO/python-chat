import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
socketio = SocketIO(app)

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

@socketio.on('envoie_message')
def handle_send_message_event(data):
    app.logger.info(f"{data['username']} a envoyé un message au room {data['room']}: {data['message']}")
    socketio.emit('recu_msg', data, room=data['room'])

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info(f"{data['username']} a rejoint le room {data['room']}")
    join_room(data['room'])
    socketio.emit('announcement_join_room', data, room=data['room'])

@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    # Relay WebRTC offer to other peer(s) in room
    socketio.emit('webrtc_offer', data, room=data['room'], include_self=False)

@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    # Relay WebRTC answer to other peer(s) in room
    socketio.emit('webrtc_answer', data, room=data['room'], include_self=False)

@socketio.on('webrtc_ice_candidate')
def handle_webrtc_ice_candidate(data):
    # Relay ICE candidate to other peer(s) in room
    socketio.emit('webrtc_ice_candidate', data, room=data['room'], include_self=False)

@socketio.on('webrtc_end_call')
def handle_webrtc_end_call(data):
    # Relay end call signal to other peer(s) in room
    socketio.emit('webrtc_end_call', data, room=data['room'], include_self=False)

if __name__ == "__main__":
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
