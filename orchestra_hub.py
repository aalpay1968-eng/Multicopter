from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'orchestra-secret-key-ffd500'
CORS(app, resources={r"/*": {"origins": "*"}})  # Tüm kaynaklara izin ver

# SocketIO ayarları: CORS açık, asenkron mod threading (Windows uyumlu)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Aktif Ajanlar Listesi
active_agents = {}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def handle_connect():
    print(f"[CONNECT] Yeni bir baglanti kabul edildi: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[DISCONNECT] Baglanti kesildi: {request.sid}")
    # Bağlantı kopan ajanı listeden temizle
    agent_to_remove = None
    for name, info in active_agents.items():
        if info.get('sid') == request.sid:
            agent_to_remove = name
            break
    if agent_to_remove:
        del active_agents[agent_to_remove]
        print(f"[CLEANUP] Ajan silindi: {agent_to_remove}")
        emit('update_agent_list', list(active_agents.keys()), broadcast=True)

@socketio.on('register')
def handle_register(data):
    agent_name = data.get('agent_name', 'Unknown')
    role = data.get('role', 'guest')
    print(f"[REGISTER] KAYIT ALINDI: {agent_name} ({role}) - SID: {request.sid}")
    
    # Ajanı listeye ekle
    active_agents[agent_name] = {
        'role': role,
        'status': 'online',
        'sid': request.sid,
        'joined_at': datetime.datetime.now().strftime("%H:%M:%S")
    }
    
    # Herkese güncel listeyi gönder
    emit('update_agent_list', list(active_agents.keys()), broadcast=True)
    
    # Kayıt yapan ajana özel onay mesajı
    emit('registration_success', {'message': f'Hosgeldin {agent_name}! Gorev bekleniyor.'})

@socketio.on('task_complete')
def handle_task_complete(data):
    print(f"[TASK_COMPLETE] GOREV TAMAMLANDI: {data}")
    emit('log_message', {'msg': f"[{data.get('agent')}] {data.get('result')}"}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    msg = data.get('message')
    sender = data.get('sender', 'Hub')
    print(f"[MSG] {sender} -> {msg}")
    # Web Arayüzü için receive_message yayını
    emit('receive_message', {'sender': sender, 'message': msg}, broadcast=True)
    # İHA İstemcileri (Agent) için standart 'message' yayını
    emit('message', msg, broadcast=True)

if __name__ == '__main__':
    print("[START] Orkestra Hub Baslatiliyor... (Port 5000)")
    print("[INFO] CORS izinleri acildi, WebSocket/Polling otomatik modu aktif.")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>FFD500 Orkestra Hub</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1e1e2e; color: #fff; margin: 0; display: flex; height: 100vh; }
        .sidebar { width: 250px; background: #252536; padding: 20px; border-right: 1px solid #333; }
        .main { flex: 1; padding: 20px; display: flex; flex-direction: column; }
        .agent-item { padding: 10px; margin-bottom: 10px; background: #333; border-radius: 5px; display: flex; align-items: center; }
        .led { width: 12px; height: 12px; border-radius: 50%; background: #555; margin-right: 10px; box-shadow: 0 0 5px #000; }
        .led.online { background: #0f0; box-shadow: 0 0 8px #0f0; }
        h2 { margin-top: 0; }
        #logs { flex: 1; background: #111; padding: 15px; overflow-y: auto; border-radius: 5px; font-family: monospace; font-size: 14px; border: 1px solid #444; }
        .log-entry { margin-bottom: 5px; border-bottom: 1px solid #333; padding-bottom: 2px; }
        .input-area { margin-top: 10px; display: flex; gap: 10px; }
        input { flex: 1; padding: 10px; border-radius: 5px; border: none; background: #333; color: #fff; }
        button { padding: 10px 20px; background: #007acc; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #005fa3; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>🤖 Aktif Ajanlar</h2>
        <div id="agent-list">
            <div style="color: #888; font-style: italic;">Bağlı ajan bekleniyor...</div>
        </div>
    </div>
    <div class="main">
        <h2>📡 Orkestra Konsolu</h2>
        <div id="logs"></div>
        <div class="input-area">
            <input type="text" id="msgInput" placeholder="Görev veya mesaj girin...">
            <button onclick="sendMessage()">Gönder</button>
        </div>
    </div>

    <script>
        // Socket bağlantısı (Otomatik olarak mevcut URL'yi kullanır)
        const socket = io(); 

        socket.on('connect', () => {
            addLog("✅ Hub'a bağlanıldı!", "system");
        });

        socket.on('update_agent_list', (agents) => {
            const listDiv = document.getElementById('agent-list');
            listDiv.innerHTML = '';
            if (agents.length === 0) {
                listDiv.innerHTML = '<div style="color: #888; font-style: italic;">Bağlı İHA bekleniyor...</div>';
            } else {
                agents.forEach(agent => {
                    listDiv.innerHTML += `
                        <div class="agent-item">
                            <div class="led online"></div>
                            <span>${agent}</span>
                        </div>`;
                });
            }
        });

        socket.on('log_message', (data) => {
            addLog(data.msg, "info");
        });
        
        socket.on('receive_message', (data) => {
            addLog(`[${data.sender}]: ${data.message}`, "chat");
        });

        function addLog(msg, type) {
            const logsDiv = document.getElementById('logs');
            const time = new Date().toLocaleTimeString();
            const color = type === 'system' ? '#0f0' : (type === 'chat' ? '#00ccff' : '#fff');
            logsDiv.innerHTML += `<div class="log-entry" style="color:${color}">[${time}] ${msg}</div>`;
            logsDiv.scrollTop = logsDiv.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('msgInput');
            const msg = input.value;
            if (msg) {
                socket.emit('send_message', { sender: 'Orkestra Şefi', message: msg });
                input.value = '';
            }
        }
    </script>
</body>
</html>
"""
