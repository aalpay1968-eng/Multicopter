import os
import datetime
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit

# --- Yapılandırma ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ffd500-orchestra-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Geçici Bellek (Veritabanı yerine) ---
# Gerçek bir üretim ortamında SQLite veya PostgreSQL kullanılmalıdır.
agents_status = {
    "Qwen_Chief": {"status": "online", "role": "Orkestra Şefi", "color": "green"},
    "Antigravity": {"status": "offline", "role": "İcraatçı / Dosya Yöneticisi", "color": "red"},
    "AI_Studio_CFD": {"status": "offline", "role": "Aerodinamik Uzmanı", "color": "red"},
    "Claude_Architect": {"status": "offline", "role": "Yapısal Tasarımcı", "color": "red"}
}

chat_history = [
    {"sender": "Sistem", "message": "Orkestra Hub başlatıldı. Hoş geldiniz.", "time": datetime.datetime.now().strftime("%H:%M")}
]

tasks = [
    {"id": "TASK_001", "desc": "CAD Dosyalarının Oluşturulması", "assigned_to": "Antigravity", "status": "completed"},
    {"id": "TASK_002", "desc": "CFD Simülasyonu", "assigned_to": "AI_Studio_CFD", "status": "pending"},
    {"id": "TASK_003", "desc": "Güç Sistemi Optimizasyonu", "assigned_to": "Qwen_Chief", "status": "in_progress"}
]

# --- HTML Arayüzü (Tek Dosya İçine Gömülü) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>FFD500 Orkestra Hub</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h2 { margin-top: 0; color: #333; }
        
        /* Agent Listesi */
        .agent-item { display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
        .led { width: 12px; height: 12px; border-radius: 50%; margin-right: 10px; display: inline-block; }
        .led.green { background-color: #2ecc71; box-shadow: 0 0 5px #2ecc71; }
        .led.red { background-color: #e74c3c; box-shadow: 0 0 5px #e74c3c; }
        .agent-info strong { display: block; }
        .agent-info small { color: #777; }

        /* Chat */
        #chat-box { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; background: #fafafa; }
        .msg { margin-bottom: 10px; padding: 8px; border-radius: 5px; }
        .msg.system { background: #e8f4fd; border-left: 4px solid #3498db; }
        .msg.user { background: #e8f8f5; border-left: 4px solid #2ecc71; text-align: right; }
        .msg.ai { background: #fff; border-left: 4px solid #9b59b6; }
        .msg-meta { font-size: 0.8em; color: #888; margin-bottom: 2px; }
        
        input[type="text"], select { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box;}
        button { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%; }
        button:hover { background: #2980b9; }
        
        /* Task List */
        .task-item { padding: 8px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
        .status-badge { padding: 2px 6px; border-radius: 4px; font-size: 0.8em; color: white; }
        .bg-completed { background: #2ecc71; }
        .bg-pending { background: #f1c40f; color: #333; }
        .bg-in_progress { background: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sol Panel: Durum ve Görevler -->
        <div>
            <div class="card" style="margin-bottom: 20px;">
                <h2>🤖 Ajan Durumu</h2>
                <div id="agent-list">
                    {% for name, info in agents.items() %}
                    <div class="agent-item">
                        <span class="led {{ info.color }}"></span>
                        <div class="agent-info">
                            <strong>{{ name }}</strong>
                            <small>{{ info.role }}</small>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="card">
                <h2>📋 Aktif Görevler</h2>
                <div id="task-list">
                    {% for task in tasks %}
                    <div class="task-item">
                        <span>{{ task.id }}: {{ task.desc }}</span>
                        <span class="status-badge bg-{{ task.status }}">{{ task.status }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Sağ Panel: Sohbet -->
        <div class="card">
            <h2>💬 Orkestra Sohbet Odası</h2>
            <div id="chat-box">
                {% for msg in chat %}
                <div class="msg {{ msg.sender|lower }}">
                    <div class="msg-meta">{{ msg.time }} - {{ msg.sender }}</div>
                    <div>{{ msg.message }}</div>
                </div>
                {% endfor %}
            </div>
            <form id="chat-form">
                <select id="target-agent">
                    <option value="All">Tüm Ajanlar</option>
                    <option value="Antigravity">Antigravity</option>
                    <option value="AI_Studio_CFD">AI Studio CFD</option>
                    <option value="Qwen_Chief">Qwen Şef</option>
                </select>
                <input type="text" id="message-input" placeholder="Mesajınızı veya görevinizi yazın..." autocomplete="off">
                <button type="submit">Gönder</button>
            </form>
        </div>
    </div>

    <script>
        const socket = io();
        const form = document.getElementById('chat-form');
        const input = document.getElementById('message-input');
        const target = document.getElementById('target-agent');
        const chatBox = document.getElementById('chat-box');

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            if (input.value) {
                socket.emit('chat_message', {
                    sender: 'User (Admin)',
                    message: input.value,
                    target: target.value
                });
                input.value = '';
            }
        });

        socket.on('new_message', (data) => {
            const div = document.createElement('div');
            div.className = `msg ${data.sender.includes('User') ? 'user' : 'ai'}`;
            div.innerHTML = `<div class="msg-meta">${data.time} - ${data.sender}</div><div>${data.message}</div>`;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        });
        
        // Periyodik durum güncellemesi (Basit polling yerine socket ile yapılabilir ama şimdilik bu yeterli)
        setInterval(() => {
            location.reload(); // Basitlik için sayfayı yenileyerek durumu güncelle
        }, 10000); 
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, agents=agents_status, chat=chat_history, tasks=tasks)

@socketio.on('connect')
def handle_connect():
    print('Kullanıcı bağlandı')

@socketio.on('chat_message')
def handle_message(data):
    # Mesajı kaydet
    new_msg = {
        "sender": data['sender'],
        "message": f"[{data['target']}] {data['message']}" if data['target'] != 'All' else data['message'],
        "time": datetime.datetime.now().strftime("%H:%M")
    }
    chat_history.append(new_msg)
    
    # Herkese yayınla
    emit('new_message', new_msg, broadcast=True)
    
    # Burada basit bir "AI Yanıtı" simülasyonu yapabiliriz
    # Gerçek senaryoda bu kısım ilgili AI'ın API'sini tetikler
    if data['target'] == 'Antigravity' or data['target'] == 'All':
        # Antigravity'nin meşgul olduğunu varsayalım
        pass 

if __name__ == '__main__':
    # Codespaces için tüm arayüzleri dinle
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)