const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());

const PORT = process.env.PORT || 5000;

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Ajan hafızası
let active_agents = {};

// Dosya yolu çözme yardımcı fonksiyonları
function getPaths() {
  const rootState = path.join(__dirname, 'ORCHESTRA_STATE.json');
  const docState = path.join(__dirname, 'FFD500', 'docs', 'ORCHESTRA_STATE.json');
  const rootLog = path.join(__dirname, 'ORCHESTRA_LOG.md');
  const docLog = path.join(__dirname, 'FFD500', 'docs', 'ORCHESTRA_LOG.md');

  return {
    statePath: fs.existsSync(docState) ? docState : (fs.existsSync(rootState) ? rootState : docState),
    logPath: fs.existsSync(docLog) ? docLog : (fs.existsSync(rootLog) ? rootLog : docLog)
  };
}

// ORCHESTRA_STATE.json dosyasını güncelle
function updateStateFile(taskDesc, status, agentName = null) {
  try {
    const { statePath } = getPaths();
    if (!fs.existsSync(statePath)) return;
    
    const content = fs.readFileSync(statePath, 'utf8');
    const state = JSON.parse(content);
    
    state.last_updated = new Date().toISOString();
    
    if (status === 'LOCKED') {
      state.system_status = 'LOCKED';
      state.locked_by = agentName || 'Yönetici';
      state.current_task = taskDesc;
      
      if (state.tasks) {
        state.tasks.push({
          id: `TASK_${Date.now()}`,
          description: taskDesc,
          status: 'PENDING',
          assigned_to: agentName || 'ANTIGRAVITY_01'
        });
      }
    } else if (status === 'COMPLETED') {
      state.system_status = 'COMPLETED';
      state.locked_by = null;
      state.current_task = null;
      
      if (state.tasks) {
        for (let i = state.tasks.length - 1; i >= 0; i--) {
          if (state.tasks[i].status === 'PENDING') {
            state.tasks[i].status = 'COMPLETED';
            break;
          }
        }
      }
    }
    
    fs.writeFileSync(statePath, JSON.stringify(state, null, 2), 'utf8');
    console.log(`[FILE] State dosyası güncellendi: ${statePath}`);
  } catch (err) {
    console.error(`[ERROR] State güncellenirken hata: ${err.message}`);
  }
}

// ORCHESTRA_LOG.md dosyasını güncelle (Reverse-kronolojik)
function appendToLogFile(title, desc, findings, nextAction) {
  try {
    const { logPath } = getPaths();
    if (!fs.existsSync(logPath)) return;
    
    let content = fs.readFileSync(logPath, 'utf8');
    const headerEnd = content.indexOf('---');
    let header = '# 📜 Orkestra İletişim Günlüğü (Orchestra Log)\n\nBu dosya, tüm AI ajanlarının birbirine bıraktığı notları, uyarıları ve görev özetlerini içerir. **Ters kronolojik sıra** ile doldurulmalıdır.\n\n---';
    let body = content;
    
    if (headerEnd !== -1) {
      header = content.substring(0, headerEnd + 3);
      body = content.substring(headerEnd + 3);
    }
    
    const timestampStr = new Date().toISOString().replace('T', ' ').substring(0, 19);
    const newEntry = `\n\n## [${timestampStr}] - ${title}\n**Görev:** ${desc}\n**Açıklama:**\n${findings}\n\n**Sonraki Eylem:**\n${nextAction}\n\n---`;
    
    fs.writeFileSync(logPath, header + newEntry + body, 'utf8');
    console.log(`[FILE] Log dosyası güncellendi: ${logPath}`);
  } catch (err) {
    console.error(`[ERROR] Log güncellenirken hata: ${err.message}`);
  }
}

const HTML_CODE = `
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FFD500 Orkestra Yönetim Merkezi (Node.js)</title>
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
        <h1>🚁 FFD500 Orkestra Yönetim Merkezi (Node.js)</h1>
        
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
            const html = \`<div class="log-entry"><span class="log-time">[\${time}]</span><span class="\${colorClass}">\${sender}:</span> \${msg}</div>\`;
            logBoxEl.innerHTML += html;
            logBoxEl.scrollTop = logBoxEl.scrollHeight;
        }

        socket.on('connect', () => {
            addLog('sys', 'Sistem', 'Hub\\\'a başarıyla bağlandı!');
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
                agentListEl.innerHTML += \`
                    <div class="agent-card">
                        <div class="status-dot"></div>
                        <div class="agent-info">
                            <span class="agent-name">\${data.name}</span>
                            <span class="agent-role">\${data.role}</span>
                        </div>
                    </div>
                \`;
            }
            addLog('sys', 'Sistem', \`Ajan listesi güncellendi: \${Object.keys(agents).length} aktif.\`);
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
`;

app.get('/', (req, res) => {
  res.send(HTML_CODE);
});

io.on('connection', (socket) => {
  console.log(`[CONNECT] Yeni bağlantı: ${socket.id}`);
  socket.emit('update_agents', active_agents);

  // Ajan Kayıt
  socket.on('register_agent', (data) => {
    const name = data.name || 'Unknown';
    const role = data.role || 'guest';
    console.log(`[REGISTER] Ajan Kayıt: ${name} (${role}) - ID: ${socket.id}`);
    
    active_agents[socket.id] = {
      name: name,
      role: role,
      time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
    };
    
    io.emit('update_agents', active_agents);
    io.emit('broadcast_msg', { sender: 'Sistem', text: `${name} (${role}) sisteme katıldı.`, type: 'sys' });
  });

  // Yönetici Komutu
  socket.on('user_command', (data) => {
    const txt = data.text;
    console.log(`[COMMAND] Yönetici Komutu: ${txt}`);
    
    // UI Loglarını besle
    io.emit('broadcast_msg', { sender: 'Yönetici', text: txt, type: 'admin' });
    
    // Ajanlara ilet
    io.emit('agent_task', { task: txt, from: 'Yönetici' });
    
    // State ve Log dosyalarını güncelle
    updateStateFile(txt, 'LOCKED', 'Antigravity');
    appendToLogFile(
      'Yönetici (Görev Atama)',
      'Yeni görev orkestra üzerinden gönderildi.',
      `- Görev: ${txt}`,
      '- Ajanın işlemi yapması ve durum bildirmesi bekleniyor.'
    );
  });

  // Ajan Cevabı
  socket.on('agent_response', (data) => {
    const name = data.agent || 'Bilinmeyen';
    const txt = data.text || '';
    console.log(`[RESPONSE] Ajan Cevabı: ${name} -> ${txt}`);
    
    // UI Loglarını besle
    io.emit('broadcast_msg', { sender: name, text: txt, type: 'agent' });
    
    // State ve Log dosyalarını güncelle
    updateStateFile(txt, 'COMPLETED');
    appendToLogFile(
      `${name} (Görev Tamamlandı)`,
      'Ajan görevi başarıyla tamamladığını bildirdi.',
      `- Sonuç/Rapor: ${txt}`,
      '- Sistem beklemede (IDLE).'
    );
  });

  // Bağlantı Kesilmesi
  socket.on('disconnect', () => {
    if (active_agents[socket.id]) {
      const name = active_agents[socket.id].name;
      console.log(`[DISCONNECT] Bağlantı kesildi: ${name} - ID: ${socket.id}`);
      
      delete active_agents[socket.id];
      io.emit('update_agents', active_agents);
      io.emit('broadcast_msg', { sender: 'Sistem', text: `${name} sistemden ayrıldı.`, type: 'sys' });
    }
  });
});

const serverInstance = server.listen(PORT, () => {
  console.log(`\n=============================================`);
  console.log(`🚀 FFD500 Node.js Hub Sunucusu Başlatıldı!`);
  console.log(`🌐 Port: ${PORT}`);
  console.log(`🔗 Web Arayüzü: http://localhost:${PORT}`);
  console.log(`=============================================\n`);
});
