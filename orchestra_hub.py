from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'orchestra_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Aktif Ajanlar Listesi
active_agents = {}

# HTML Arayüz Şablonu (Güncellendi: JS ile dinamik liste)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FFD500 Orkestra Hub</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; padding: 20px; }
        .container { display: flex; gap: 20px; }
        .panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); flex: 1; }
        h2 { color: #333; }
        .agent-item { display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
        .led { width: 12px; height: 12px; border-radius: 50%; margin-right: 10px; background: #ccc; }
        .led.active { background: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
        .chat-box { height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; }
        .msg { margin-bottom: 5px; }
        .msg.system { color: #666; font-style: italic; }
        .msg.user { color: #007bff; }
        .msg.agent { color: #28a745; }
        input, button { padding: 10px; width: 100%; margin-top: 5px; box-sizing: border-box; }
    </style>
</head>
<body>
    <h1>🚁 FFD500 Orkestra Kontrol Merkezi</h1>
    <div class="container">
        <!-- Ajan Listesi -->
        <div class="panel">
            <h2>🤖 Aktif Ajanlar</h2>
            <div id="agent-list">
                <p>Bekleniyor...</p>
            </div>
        </div>
        
        <!-- Sohbet ve Görev -->
        <div class="panel">
            <h2>💬 Görev ve İletişim</h2>
            <div id="chat" class="chat-box"></div>
            <input type="text" id="msg-input" placeholder="Görev veya mesaj yazın...">
            <button onclick="sendMessage()">Gönder</button>
        </div>
    </div>

    <script>
        const socket = io();
        const chatBox = document.getElementById('chat');
        const agentListDiv = document.getElementById('agent-list');

        // Mesajları Dinle
        socket.on('message', (data) => {
            const div = document.createElement('div');
            div.className = `msg ${data.type}`;
            div.innerText = `[${data.time}] ${data.text}`;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        });

        // Ajan Listesini Güncelle
        socket.on('update_agents', (agents) => {
            agentListDiv.innerHTML = '';
            if (Object.keys(agents).length === 0) {
                agentListDiv.innerHTML = '<p>Aktif ajan yok.</p>';
                return;
            }
            for (const [name, info] of Object.entries(agents)) {
                const div = document.createElement('div');
                div.className = 'agent-item';
                const ledClass = info.status === 'active' ? 'led active' : 'led';
                div.innerHTML = `<div class="${ledClass}"></div><strong>${name}</strong> <small>(${info.role})</small>`;
                agentListDiv.appendChild(div);
            }
        });

        function sendMessage() {
            const input = document.getElementById('msg-input');
            const text = input.value;
            if (text) {
                socket.emit('user_message', { text: text });
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
    print("✅ Yeni bir istemci bağlandı.")
    # Bağlanan herkese mevcut ajan listesini gönder
    emit('update_agents', active_agents)

@socketio.on('disconnect')
def handle_disconnect():
    print("❌ Bir istemci ayrıldı.")

# --- KRİTİK KISIM: Ajan Kaydı ---
@socketio.on('register')
def handle_register(data):
    agent_name = data.get('agent_name', 'Bilinmeyen')
    role = data.get('role', 'general')
    print(f"📥 KAYIT ALINDI: {agent_name} ({role})")
    
    # Ajanı listeye ekle
    active_agents[agent_name] = {
        'role': role,
        'status': 'active',
        'joined': str(datetime.datetime.now())
    }
    
    # Herkese güncel listeyi gönder
    socketio.emit('update_agents', active_agents)
    
    # Sisteme bilgi mesajı at
    socketio.emit('message', {
        'type': 'system',
        'time': datetime.datetime.now().strftime('%H:%M'),
        'text': f'{agent_name} sisteme katıldı.'
    })

@socketio.on('user_message')
def handle_user_message(data):
    text = data.get('text')
    print(f"👤 Kullanıcı Mesajı: {text}")
    socketio.emit('message', {
        'type': 'user',
        'time': datetime.datetime.now().strftime('%H:%M'),
        'text': f'Yönetici: {text}'
    })
    # Burada tüm ajanlara 'task_assignment' emit edilebilir
    socketio.emit('task_assignment', {
        'from': 'Admin',
        'content': text
    })

if __name__ == '__main__':
    print("🚀 Orkestra Hub başlatılıyor... http://0.0.0.0:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
