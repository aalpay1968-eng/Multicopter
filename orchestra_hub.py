from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import datetime
import sys

# Windows terminal emoji çökmesini önlemek için UTF-8 stdout yapılandırması
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ffd500-fixed-secret'
CORS(app, origins="*")

# Dinamik eventlet tespiti ve fallback modu
try:
    import eventlet
    async_mode = 'eventlet'
except ImportError:
    async_mode = 'threading'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode)

agents = {}

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>FFD500 Orkestra Hub (Fixed)</title>
    <style>
        body { background: #1e1e2e; color: #fff; font-family: 'Segoe UI', sans-serif; padding: 20px; margin: 0; }
        .container { max-width: 900px; margin: 0 auto; }
        .panel { background: #2b2b3b; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        h1 { color: #4cc9f0; text-align: center; margin-top: 0; }
        h3 { margin-top: 0; color: #ddd; border-bottom: 1px solid #444; padding-bottom: 10px; }
        
        /* Ajan Listesi */
        #agent-list { list-style: none; padding: 0; min-height: 50px; }
        .agent-item { background: #32324a; padding: 12px; margin-bottom: 8px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #00ff88; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        .status-dot { height: 10px; width: 10px; background: #00ff88; border-radius: 50%; display: inline-block; margin-right: 10px; box-shadow: 0 0 6px #00ff88; }
        
        /* Log Alanı */
        #log-box { background: #000; color: #00ff88; padding: 15px; height: 250px; overflow-y: auto; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 13px; border: 1px solid #333; }
        .log-entry { margin-bottom: 5px; border-bottom: 1px solid #222; padding-bottom: 2px; }
        .log-time { color: #888; margin-right: 8px; }
        .log-admin { color: #4cc9f0; font-weight: bold; }
        .log-agent { color: #00ff88; font-weight: bold; }

        /* Giriş Alanı */
        .input-group { display: flex; gap: 10px; }
        input { flex: 1; padding: 12px; border-radius: 6px; border: none; background: #404055; color: white; font-size: 15px; outline: none; }
        input:focus { background: #4a4a60; }
        button { padding: 12px 25px; background: #4cc9f0; color: #000; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 15px; transition: 0.2s; }
        button:hover { background: #3db5dc; transform: translateY(-2px); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚁 FFD500 Orkestra Yönetim Merkezi</h1>
        
        <div class="panel">
            <h3>🟢 Aktif Ajanlar</h3>
            <ul id="agent-list"><li style="color:#888; text-align:center;">Bağlantı bekleniyor...</li></ul>
        </div>

        <div class="panel">
            <h3>📡 Görev & Sohbet</h3>
            <div class="input-group">
                <input type="text" id="msg-input" placeholder="Görev yazın (Örn: Kanat analizi yap)...">
                <button onclick="sendTask()">GÖNDER</button>
            </div>
        </div>

        <div class="panel">
            <h3>📜 Canlı Sistem Logları</h3>
            <div id="log-box"></div>
        </div>
    </div>

    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script>
        const socket = io();
        const agentList = document.getElementById('agent-list');
        const logBox = document.getElementById('log-box');
        const msgInput = document.getElementById('msg-input');

        function addLog(agent, text, type='info') {
            const time = new Date().toLocaleTimeString();
            const div = document.createElement('div');
            div.className = 'log-entry';
            
            let agentSpan = '';
            if(agent === 'Sistem') agentSpan = `<span class="log-time">[${time}]</span>`;
            else if(agent === 'Yönetici') agentSpan = `<span class="log-time">[${time}]</span><span class="log-admin">${agent}:</span>`;
            else agentSpan = `<span class="log-time">[${time}]</span><span class="log-agent">${agent}:</span>`;
            
            div.innerHTML = `${agentSpan} ${text}`;
            logBox.appendChild(div);
            logBox.scrollTop = logBox.scrollHeight;
        }

        socket.on('connect', () => addLog('Sistem', 'Hub\'a başarıyla bağlandı.', 'success'));
        socket.on('disconnect', () => addLog('Sistem', 'Bağlantı kesildi.', 'error'));

        // Ajan Listesi Güncelleme
        socket.on('update_list', (data) => {
            agentList.innerHTML = '';
            const count = Object.keys(data).length;
            if (count === 0) {
                agentList.innerHTML = '<li style="color:#888; text-align:center; padding:10px;">Henüz bağlı ajan yok.</li>';
                return;
            }
            for (const [sid, info] of Object.entries(data)) {
                const li = document.createElement('li');
                li.className = 'agent-item';
                li.innerHTML = `
                    <span><span class="status-dot"></span><strong>${info.name}</strong> <small style="color:#aaa">(${info.role})</small></span>
                    <small style="color:#aaa">${info.time}</small>
                `;
                agentList.appendChild(li);
            }
            addLog('Sistem', `${count} ajan aktif.`, 'info');
        });

        // Yeni Mesaj Gösterme (Hem Yönetici hem Ajan)
        socket.on('new_msg', (data) => {
            addLog(data.agent, data.text);
        });

        // Görev Gönderme
        function sendTask() {
            const txt = msgInput.value.trim();
            if(!txt) return;
            // Hub'ın dinlediği 'task' olayını gönderiyoruz
            socket.emit('task', {text: txt});
            addLog('Yönetici', txt);
            msgInput.value = '';
        }

        msgInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendTask();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@socketio.on('connect')
def on_connect():
    print(f"✅ Bağlantı: {request.sid}")
    emit('update_list', agents)

@socketio.on('register')
def on_register(data):
    name = data.get('agent_name', 'Unknown')
    role = data.get('role', 'guest')
    print(f"📥 KAYIT: {name} ({role})")
    agents[request.sid] = {'name': name, 'role': role, 'time': datetime.datetime.now().strftime("%H:%M")}
    emit('update_list', agents, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    if request.sid in agents:
        name = agents[request.sid]['name']
        print(f"❌ KOPDU: {name}")
        del agents[request.sid]
        emit('update_list', agents, broadcast=True)

# --- KRİTİK GÖREV YÖNLENDİRMELERİ ---

@socketio.on('task')
def on_task(data):
    txt = data.get('text')
    print(f"📢 GÖREV: {txt}")
    # 1. Ekrana yazdır (Web UI)
    emit('new_msg', {'agent': 'Yönetici', 'text': txt}, broadcast=True)
    # 2. Ajanın dinlediği 'message' olayını fırlat
    emit('message', {'message': txt, 'from': 'Orkestra Şefi'}, broadcast=True)

# Ajan 'task_complete' gönderirse
@socketio.on('task_complete')
def on_task_complete(data):
    agent = data.get('agent', 'Bilinmeyen')
    result = data.get('result', '')
    log = data.get('log', '')
    text = f"{result} - {log}" if log else result
    print(f"✅ TAMAMLANDI: {agent} -> {text}")
    emit('new_msg', {'agent': agent, 'text': text}, broadcast=True)

# Ajan 'message' gönderirse (Onay vb.)
@socketio.on('message')
def on_message_from_agent(data):
    agent = data.get('agent', data.get('from', 'Bilinmeyen Ajan'))
    text = data.get('text', data.get('message', data.get('result', '')))
    print(f"💬 MESAJ: {agent} -> {text}")
    emit('new_msg', {'agent': agent, 'text': text}, broadcast=True)

if __name__ == '__main__':
    print("🚀 FFD500 Hub Başlatılıyor...")
    print(f"⚠️ WebSocket Modu: {async_mode.upper()}")
    print("⚠️ Dinlenen Olaylar: task, register, message, task_complete")
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True, debug=False)
