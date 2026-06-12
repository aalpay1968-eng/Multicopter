from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'orchestra_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Aktif Ajanlar Listesi (Bellekte tutulur)
active_agents = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FFD500 Orkestra Hub</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; display: flex; gap: 20px; }
        .panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); flex: 1; }
        .agent-list { list-style: none; padding: 0; }
        .agent-item { display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
        .led { width: 12px; height: 12px; border-radius: 50%; margin-right: 10px; background: #ccc; }
        .led.active { background: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
        .led.inactive { background: #e74c3c; }
        #chat-log { height: 300px; overflow-y: scroll; border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; background: #fafafa; }
        .msg { margin-bottom: 5px; }
        .msg.system { color: #666; font-style: italic; }
        .msg.agent { color: #2980b9; font-weight: bold; }
        .msg.user { color: #27ae60; font-weight: bold; }
        input[type="text"] { width: 70%; padding: 10px; }
        button { padding: 10px 20px; background: #3498db; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🚁 FFD500 Orkestra Kontrol Merkezi</h1>
    <div class="container">
        <div class="panel">
            <h2>🤖 Aktif Ajanlar</h2>
            <ul class="agent-list" id="agent-list">
                <!-- Ajanlar buraya dinamik gelecek -->
            </ul>
        </div>
        <div class="panel">
            <h2>💬 Görev & Sohbet</h2>
            <div id="chat-log"></div>
            <input type="text" id="msg-input" placeholder="Görev yazın...">
            <button onclick="sendMessage()">Gönder</button>
        </div>
    </div>

    <script>
        const socket = io();
        const agentListEl = document.getElementById('agent-list');
        const chatLogEl = document.getElementById('chat-log');

        socket.on('connect', () => console.log('✅ Arayüz Hub\'a bağlı'));

        // Ajan listesi güncellendiğinde
        socket.on('update_agents', (agents) => {
            agentListEl.innerHTML = '';
            for (const [name, data] of Object.entries(agents)) {
                const li = document.createElement('li');
                li.className = 'agent-item';
                const statusClass = data.status === 'active' ? 'active' : 'inactive';
                li.innerHTML = `<div class="led ${statusClass}"></div> <strong>${name}</strong> <small>(${data.role})</small>`;
                agentListEl.appendChild(li);
            }
        });

        // Yeni mesaj geldiğinde
        socket.on('new_message', (msg) => {
            const div = document.createElement('div');
            div.className = `msg ${msg.type}`;
            div.innerText = `[${msg.time}] ${msg.sender}: ${msg.text}`;
            chatLogEl.appendChild(div);
            chatLogEl.scrollTop = chatLogEl.scrollHeight;
        });

        function sendMessage() {
            const input = document.getElementById('msg-input');
            if (input.value.trim() !== '') {
                socket.emit('user_message', { text: input.value });
                input.value = '';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def handle_connect():
    print("🔌 Yeni bir bağlantı kabul edildi.")
    emit('update_agents', active_agents)

@socketio.on('register')
def handle_register(data):
    agent_name = data.get('agent_name', 'Unknown')
    role = data.get('role', 'general')
    print(f"📥 KAYIT ALINDI: {agent_name} ({role})")
    
    active_agents[agent_name] = {
        'role': role,
        'status': 'active',
        'last_seen': datetime.now().isoformat()
    }
    
    # Tüm bağlı istemcilere (arayüz dahil) güncel listeyi gönder
    emit('update_agents', active_agents, broadcast=True)
    
    # Sohbet loguna bilgi düş
    emit('new_message', {
        'type': 'system',
        'sender': 'Sistem',
        'time': datetime.now().strftime('%H:%M'),
        'text': f'{agent_name} sisteme katıldı.'
    }, broadcast=True)

@socketio.on('user_message')
def handle_user_message(data):
    msg_text = data.get('text')
    print(f"👤 Kullanıcı Mesajı: {msg_text}")
    
    emit('new_message', {
        'type': 'user',
        'sender': 'Yönetici',
        'time': datetime.now().strftime('%H:%M'),
        'text': msg_text
    }, broadcast=True)
    
    # Tüm ajanlara görev olarak ilet
    emit('task_assignment', {
        'from': 'Yönetici',
        'text': msg_text,
        'timestamp': datetime.now().isoformat()
    }, broadcast=True)

@socketio.on('task_complete')
def handle_task_complete(data):
    agent = data.get('agent')
    result = data.get('result')
    print(f"✅ Görev Tamamlandı: {agent} - {result}")
    
    emit('new_message', {
        'type': 'agent',
        'sender': agent,
        'time': datetime.now().strftime('%H:%M'),
        'text': result
    }, broadcast=True)

if __name__ == '__main__':
    print("🚀 Orkestra Hub başlatılıyor... http://0.0.0.0:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
