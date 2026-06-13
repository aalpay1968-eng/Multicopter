try:
    import eventlet
    eventlet.monkey_patch()
    async_mode = 'eventlet'
except ImportError:
    async_mode = 'threading'

import os
import sys
import socket
import datetime
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# Windows terminal encoding safety
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ffd500-secret-2026'
CORS(app, resources={r"/*": {"origins": "*"}})

socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode, logger=False, engineio_logger=False)

active_agents = {}

HTML_CODE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FFD500 Orkestra Yönetim Merkezi (Python Fallback)</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --text: #f1f5f9; --accent: #38bdf8; --success: #4ade80; --danger: #f87171; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; display: flex; justify-content: center; }
        .dashboard { width: 100%; max-width: 900px; display: grid; gap: 20px; }
        .card { background: var(--card); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #334155; }
        h1, h2 { margin: 0 0 15px 0; color: var(--accent); font-weight: 600; }
        h1 { text-align: center; font-size: 1.8rem; text-transform: uppercase; letter-spacing: 1px; }
        
        .agent-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }
        .agent-card { background: #334155; padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px; animation: fadeIn 0.3s ease; }
        .status-dot { width: 10px; height: 10px; background: var(--success); border-radius: 50%; box-shadow: 0 0 8px var(--success); animation: pulse 2s infinite; }
        .agent-info { display: flex; flex-direction: column; }
        .agent-name { font-weight: bold; font-size: 0.95rem; }
        .agent-role { font-size: 0.75rem; color: #94a3b8; }
        
        .chat-box { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; outline: none; }
        input[type="text"]:focus { border-color: var(--accent); }
        button { padding: 12px 24px; background: var(--accent); color: #0f172a; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:hover { background: #0ea5e9; transform: translateY(-1px); }
        
        .log-container { height: 250px; overflow-y: auto; background: #000; border-radius: 6px; padding: 10px; font-family: 'Courier New', monospace; font-size: 0.85rem; border: 1px solid #334155; }
        .log-entry { margin-bottom: 6px; border-bottom: 1px solid #1e293b; padding-bottom: 4px; }
        .log-time { color: #64748b; margin-right: 8px; }
        .log-admin { color: var(--accent); font-weight: bold; }
        .log-agent { color: var(--success); font-weight: bold; }
        .log-sys { color: #fbbf24; font-style: italic; }

        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>🚁 FFD500 Orkestra Yönetim Merkezi (Python Fallback)</h1>
        
        <div class="card">
            <h2>🟢 Aktif Ajanlar (<span id="count">0</span>)</h2>
            <div id="agentList" class="agent-grid">
                <div style="color:#64748b; grid-column: 1/-1; text-align:center;">Bağlantı bekleniyor...</div>
            </div>
        </div>

        <div class="card">
            <h2>📡 Görev & İletişim</h2>
            <div class="chat-box">
                <input type="text" id="msgInput" placeholder="Görev yazın (Örn: Kanat analizi yap)..." onkeypress="if(event.key==='Enter') sendMsg()">
                <button onclick="sendMsg()">GÖNDER</button>
            </div>
        </div>

        <div class="card">
            <h2>📜 Sistem Logları</h2>
            <div id="logBox" class="log-container"></div>
        </div>
    </div>

    <script>
        const socket = io({ transports: ['websocket', 'polling'], reconnection: true, reconnectionAttempts: 5 });
        
        const agentListEl = document.getElementById('agentList');
        const countEl = document.getElementById('count');
        const logBoxEl = document.getElementById('logBox');
        const msgInput = document.getElementById('msgInput');

        function addLog(type, sender, msg) {
            const time = new Date().toLocaleTimeString();
            let colorClass = type === 'admin' ? 'log-admin' : (type === 'agent' ? 'log-agent' : 'log-sys');
            const html = `<div class="log-entry"><span class="log-time">[${time}]</span><span class="${colorClass}">${sender}:</span> ${msg}</div>`;
            logBoxEl.innerHTML += html;
            logBoxEl.scrollTop = logBoxEl.scrollHeight;
        }

        socket.on('connect', () => {
            addLog('sys', 'Sistem', 'Hub\'a başarıyla bağlandı!');
        });

        socket.on('disconnect', () => {
            addLog('sys', 'Sistem', 'Bağlantı kesildi. Yeniden deneniyor...');
        });

        socket.on('update_agents', (agents) => {
            agentListEl.innerHTML = '';
            countEl.innerText = Object.keys(agents).length;
            
            if (Object.keys(agents).length === 0) {
                agentListEl.innerHTML = '<div style="color:#64748b; grid-column: 1/-1; text-align:center;">Aktif ajan yok.</div>';
                return;
            }

            for (const [sid, data] of Object.entries(agents)) {
                agentListEl.innerHTML += `
                    <div class="agent-card">
                        <div class="status-dot"></div>
                        <div class="agent-info">
                            <span class="agent-name">${data.name}</span>
                            <span class="agent-role">${data.role}</span>
                        </div>
                    </div>
                `;
            }
            addLog('sys', 'Sistem', `Ajan listesi güncellendi: ${Object.keys(agents).length} aktif.`);
        });

        socket.on('broadcast_msg', (data) => {
            addLog(data.type === 'admin' ? 'admin' : 'agent', data.sender, data.text);
        });

        function sendMsg() {
            const txt = msgInput.value.trim();
            if (!txt) return;
            socket.emit('user_command', { text: txt });
            addLog('admin', 'Yönetici', txt);
            msgInput.value = '';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@socketio.on('connect')
def handle_connect():
    print(f"✅ Bağlantı: {request.sid}")
    emit('update_agents', active_agents)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_agents:
        name = active_agents[request.sid]['name']
        print(f"❌ Kopuş: {name}")
        del active_agents[request.sid]
        emit('update_agents', active_agents, broadcast=True)

@socketio.on('register_agent')
def handle_register(data):
    name = data.get('name', 'Unknown')
    role = data.get('role', 'guest')
    print(f"📥 KAYIT: {name} ({role})")
    
    active_agents[request.sid] = {'name': name, 'role': role, 'time': datetime.datetime.now().strftime("%H:%M")}
    emit('update_agents', active_agents, broadcast=True)
    emit('broadcast_msg', {'sender': 'Sistem', 'text': f'{name} sisteme katıldı.', 'type': 'sys'}, broadcast=True)

@socketio.on('user_command')
def handle_command(data):
    txt = data.get('text')
    print(f"📢 KOMUT: {txt}")
    emit('broadcast_msg', {'sender': 'Yönetici', 'text': txt, 'type': 'admin'}, broadcast=True)
    emit('agent_task', {'task': txt, 'from': 'Yönetici'}, broadcast=True)

@socketio.on('agent_response')
def handle_response(data):
    name = data.get('agent', 'Bilinmeyen')
    txt = data.get('text', '')
    print(f"✅ CEVAP: {name} -> {txt}")
    emit('broadcast_msg', {'sender': name, 'text': txt, 'type': 'agent'}, broadcast=True)

if __name__ == '__main__':
    host_name = socket.gethostname()
    local_ip = socket.gethostbyname(host_name)
    print(f"🚀 FFD500 Python Hub Fallback Başlatılıyor...")
    print(f"🌐 Yerel IP: {local_ip}")
    print(f"🔗 Erişim: http://0.0.0.0:5000")
    print(f"⚠️ Asenkron WebSocket Modu: {async_mode.upper()}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
