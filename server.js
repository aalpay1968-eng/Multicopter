const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5000;

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Ajan hafızası ve durum takibi
let active_agents = {};

// Dosya yolları bulucu
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

// ORCHESTRA_LOG.md dosyasından geçmişi yükle
function loadLogHistory() {
  try {
    const { logPath } = getPaths();
    if (!fs.existsSync(logPath)) return [];
    
    const content = fs.readFileSync(logPath, 'utf8');
    const parts = content.split('## ');
    const history = [];
    
    for (let i = 1; i < parts.length; i++) {
      const block = parts[i].trim();
      if (!block) continue;
      
      const lines = block.split('\n');
      const headerLine = lines[0];
      
      const timeMatch = headerLine.match(/\[(.*?)\]/);
      const timestamp = timeMatch ? timeMatch[1] : '';
      
      const restHeader = headerLine.replace(/\[.*?\]/, '').replace('-', '').trim();
      const senderMatch = restHeader.match(/^(.*?)(?:\s+\(|\s*$)/);
      const sender = senderMatch ? senderMatch[1].trim() : 'Sistem';
      
      const bodyLines = lines.slice(1).map(l => l.trim()).filter(l => l.length > 0 && l !== '---');
      const body = bodyLines.join(' ');
      
      const cleanBody = body.replace(/\*\*/g, '').replace(/^- /g, '');
      
      // Kanal tespiti (Varsayılan: #general)
      let channel = '#general';
      const bodyLower = cleanBody.toLowerCase();
      if (bodyLower.includes('tasarım') || bodyLower.includes('design')) {
        channel = '#design';
      } else if (bodyLower.includes('simülasyon') || bodyLower.includes('simulation') || bodyLower.includes('termal')) {
        channel = '#simulation';
      } else if (bodyLower.includes('rapor') || bodyLower.includes('report') || bodyLower.includes('yazım')) {
        channel = '#reporting';
      }
      
      let type = 'sys';
      if (sender.toLowerCase().includes('yönetici') || sender.toLowerCase().includes('admin') || sender.toLowerCase().includes('chief')) {
        type = 'admin';
      } else if (sender.toLowerCase().includes('antigravity') || sender.toLowerCase().includes('agent') || sender.toLowerCase().includes('bot') || sender.toLowerCase().includes('specialist') || sender.toLowerCase().startsWith('ai_')) {
        type = 'agent';
      }
      
      history.push({
        time: timestamp.split(' ')[1] || timestamp,
        sender: sender,
        text: cleanBody,
        type: type,
        channel: channel
      });
    }
    
    return history.reverse(); // Kronolojik sıra
  } catch (err) {
    console.error(`[ERROR] Log geçmişi yüklenirken hata: ${err.message}`);
    return [];
  }
}

// ORCHESTRA_STATE.json dosyasından görevleri yükle
function loadStateTasks() {
  try {
    const { statePath } = getPaths();
    if (!fs.existsSync(statePath)) return [];
    
    const content = fs.readFileSync(statePath, 'utf8');
    const state = JSON.parse(content);
    return state.pending_tasks || state.tasks || [];
  } catch (err) {
    console.error(`[ERROR] Görevler yüklenirken hata: ${err.message}`);
    return [];
  }
}

// ORCHESTRA_STATE.json dosyasını güncelle
function updateStateFile(taskDesc, status, agentName = null) {
  try {
    const { statePath } = getPaths();
    if (!fs.existsSync(statePath)) return;
    
    const content = fs.readFileSync(statePath, 'utf8');
    const state = JSON.parse(content);
    
    state.last_updated = new Date().toISOString();
    state.last_updated_by = agentName || 'Yönetici';
    
    if (!state.pending_tasks) state.pending_tasks = [];
    
    if (status === 'LOCKED') {
      state.system_status = 'READY'; // workflow is running
      state.locked_by = agentName;
      state.current_agent = agentName;
      state.next_agent = agentName;
      
      // Mükerrer görev kontrolü
      const taskExists = state.pending_tasks.some(t => t.description === taskDesc && t.status === 'PENDING');
      if (!taskExists) {
        state.pending_tasks.push({
          id: `TASK_00${state.pending_tasks.length + 1}`,
          description: taskDesc,
          status: 'PENDING',
          assigned_to: agentName || 'AI_01_DESIGN'
        });
      }
    } else if (status === 'COMPLETED') {
      state.system_status = 'COMPLETED';
      state.locked_by = null;
      state.current_agent = null;
      
      // Son aktif pending görevi tamamla
      for (let i = state.pending_tasks.length - 1; i >= 0; i--) {
        if (state.pending_tasks[i].status === 'PENDING') {
          state.pending_tasks[i].status = 'COMPLETED';
          break;
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

// Görev iletme fonksiyonu
function emitTaskToAgent(assignee, taskText, channel) {
  let targetSid = null;
  for (const [sid, info] of Object.entries(active_agents)) {
    if (info.name === assignee) {
      targetSid = sid;
      break;
    }
  }

  if (targetSid) {
    io.to(targetSid).emit('agent_task', { task: taskText, from: 'Yönetici', channel: channel });
    console.log(`[TASK_EMIT] Görev ${assignee} (${targetSid}) ajanına gönderildi.`);
  } else {
    // Ajan doğrudan bağlı değilse bile odaya yayınla
    io.emit('agent_task', { task: taskText, from: 'Yönetici', channel: channel });
    console.log(`[TASK_EMIT] Ajan bulunamadı. Görev tüm odalara yayınlandı.`);
  }
}

// Ajan pingleme ve sağlık takip döngüsü (10 saniyede bir çalışır)
setInterval(() => {
  const now = Date.now();
  let changed = false;
  
  for (const [sid, agent] of Object.entries(active_agents)) {
    const diff = now - agent.lastSeen;
    let oldStatus = agent.status;
    
    if (diff > 25000) {
      agent.status = 'DEAD';
      console.log(`[DEAD] Ajan pingleme kesildi: ${agent.name} (ID: ${sid})`);
      delete active_agents[sid];
      changed = true;
    } else if (diff > 12000) {
      agent.status = 'IDLE';
      if (oldStatus !== 'IDLE') changed = true;
    } else {
      agent.status = 'HEALTHY';
      if (oldStatus !== 'HEALTHY') changed = true;
    }
  }
  
  if (changed) {
    io.emit('update_agents', active_agents);
  }
}, 3000);

// --- REST API ENDPOINTS ---
app.get('/api/health', (req, res) => {
  res.json({
    status: "ok",
    timestamp: new Date().toISOString(),
    active_agents_count: Object.keys(active_agents).length,
    agents: active_agents
  });
});

app.get('/api/tasks', (req, res) => {
  res.json(loadStateTasks());
});

app.get('/api/messages', (req, res) => {
  res.json(loadLogHistory());
});

app.post('/api/messages', (req, res) => {
  const { sender, text, channel } = req.body;
  if (!sender || !text) {
    return res.status(400).json({ error: "sender ve text parametreleri zorunludur." });
  }
  
  const ch = channel || '#general';
  const type = sender.toLowerCase().includes('ai_') ? 'agent' : 'admin';
  const msgObj = {
    sender,
    text,
    type,
    channel: ch,
    time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
  };
  
  io.emit('broadcast_msg', msgObj);
  console.log(`[REST_MSG] ${sender} (${ch}): ${text}`);
  
  // State dosyalarını tetikle
  if (type === 'agent') {
    updateStateFile(text, 'COMPLETED');
    appendToLogFile(`${sender} (REST API Cevabı)`, 'Ajan API üzerinden yanıt gönderdi.', `- Bulgular: ${text}`, '- Sistem IDLE.');
  } else {
    // Kanal ismine göre ajanı belirle
    let assignee = 'AI_01_DESIGN';
    if (ch === '#simulation') assignee = 'AI_02_SIMULATION';
    else if (ch === '#reporting') assignee = 'AI_03_REPORTING';
    
    updateStateFile(text, 'LOCKED', assignee);
    appendToLogFile(`Yönetici (REST API - ${ch})`, 'Yönetici API üzerinden komut gönderdi.', `- Komut: ${text}`, `- ${assignee} ajanının çalışması bekleniyor.`);
    
    // Ajanı WebSocket ile tetikle!
    emitTaskToAgent(assignee, text, ch);
  }
  
  io.emit('load_tasks', loadStateTasks());
  res.json({ status: "success", message: msgObj });
});

app.get('/', (req, res) => {
  const htmlPath = path.join(__dirname, 'dashboard.html');
  if (fs.existsSync(htmlPath)) {
    res.sendFile(htmlPath);
  } else {
    res.status(404).send('dashboard.html not found.');
  }
});

io.on('connection', (socket) => {
  console.log(`[CONNECT] Yeni bağlantı: ${socket.id}`);
  
  // İlk bağlantıda ajan listesini, sohbet geçmişini ve görevleri yükle
  socket.emit('update_agents', active_agents);
  socket.emit('load_history', loadLogHistory());
  socket.emit('load_tasks', loadStateTasks());

  // Ajan Tescili ve Heartbeat (register_agent)
  socket.on('register_agent', (data) => {
    const name = data.name || 'Unknown';
    const role = data.role || 'guest';
    console.log(`[REGISTER] Ajan Kayıt: ${name} (${role}) - ID: ${socket.id}`);
    
    active_agents[socket.id] = {
      name: name,
      role: role,
      status: 'HEALTHY',
      lastSeen: Date.now(),
      time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
    };
    
    io.emit('update_agents', active_agents);
    io.emit('broadcast_msg', { sender: 'Sistem', text: `${name} (${role}) sisteme katıldı.`, type: 'sys', channel: '#general', time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }) });
  });

  // Periyodik Heartbeat Pinglemesi (ping_heartbeat)
  socket.on('ping_heartbeat', (data) => {
    const name = data.name || 'Unknown';
    if (active_agents[socket.id]) {
      active_agents[socket.id].lastSeen = Date.now();
      active_agents[socket.id].status = 'HEALTHY';
    } else {
      // Yeniden tescil et
      active_agents[socket.id] = {
        name: name,
        role: data.role || 'guest',
        status: 'HEALTHY',
        lastSeen: Date.now(),
        time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
      };
      io.emit('update_agents', active_agents);
    }
  });

  // Arayüzden Görev Atama (create_task)
  socket.on('create_task', (data) => {
    const text = data.text;
    const assignee = data.assignee || 'AI_01_DESIGN';
    const channel = data.channel || '#design';
    console.log(`[TASK_CREATE] Görev oluşturuldu -> Alıcı: ${assignee}, Görev: ${text}`);

    // UI'daki kanala ve general kanala yazdır
    const timeStr = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
    const msgObj = { sender: 'Yönetici', text: `[GÖREV ATAMA -> ${assignee}]: ${text}`, type: 'admin', channel: channel, time: timeStr };
    
    io.emit('broadcast_msg', msgObj);
    if (channel !== '#general') {
      io.emit('broadcast_msg', { ...msgObj, channel: '#general' });
    }

    // Ajanı tetikle
    emitTaskToAgent(assignee, text, channel);

    // State ve Log dosyalarını güncelle
    updateStateFile(text, 'LOCKED', assignee);
    appendToLogFile(
      `Yönetici (Görev Dağıtımı - ${channel})`,
      `Görev ${assignee} ajanına atandı.`,
      `- Görev: ${text}\n- Görevli: ${assignee}`,
      '- Ajanın işlemi yapması ve durum bildirmesi bekleniyor.'
    );

    // Güncel görev listesini arayüze bas
    io.emit('load_tasks', loadStateTasks());
  });

  // Arayüzden Genel Mesaj Gönderme (user_command)
  socket.on('user_command', (data) => {
    const txt = data.text;
    console.log(`[COMMAND] Genel Komut: ${txt}`);
    
    const timeStr = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
    io.emit('broadcast_msg', { sender: 'Yönetici', text: txt, type: 'admin', channel: '#general', time: timeStr });
    
    // Tüm ajanlara genel yayın yap
    io.emit('agent_task', { task: txt, from: 'Yönetici', channel: '#general' });
    
    // State ve Log dosyalarını güncelle
    updateStateFile(txt, 'LOCKED', 'AI_01_DESIGN');
    appendToLogFile(
      'Yönetici (Genel Talimat)',
      'Tüm ajanlara genel talimat gönderildi.',
      `- Mesaj: ${txt}`,
      '- Ajanların işlemi yapması bekleniyor.'
    );

    // Görev listesini tazele
    io.emit('load_tasks', loadStateTasks());
  });

  // Ajan Cevabı (agent_response)
  socket.on('agent_response', (data) => {
    const name = data.agent || 'Bilinmeyen';
    const txt = data.text || '';
    const channel = data.channel || '#general';
    console.log(`[RESPONSE] Ajan Cevabı: ${name} -> ${txt}`);
    
    // UI Loglarını besle
    const timeStr = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
    const msgObj = { sender: name, text: txt, type: 'agent', channel: channel, time: timeStr };
    io.emit('broadcast_msg', msgObj);
    if (channel !== '#general') {
      io.emit('broadcast_msg', { ...msgObj, channel: '#general' });
    }
    
    // State ve Log dosyalarını güncelle
    updateStateFile(txt, 'COMPLETED');
    appendToLogFile(
      `${name} (Görev Tamamlandı)`,
      'Ajan görevi başarıyla tamamladığını bildirdi.',
      `- Sonuç/Rapor: ${txt}`,
      '- Sistem beklemede (IDLE).'
    );

    // Güncel görevleri ve geçmişi yeniden yükle
    io.emit('load_tasks', loadStateTasks());
  });

  // Bağlantı Kesilmesi (disconnect)
  socket.on('disconnect', () => {
    if (active_agents[socket.id]) {
      const name = active_agents[socket.id].name;
      console.log(`[DISCONNECT] Bağlantı kesildi: ${name} - ID: ${socket.id}`);
      
      delete active_agents[socket.id];
      io.emit('update_agents', active_agents);
      io.emit('broadcast_msg', { sender: 'Sistem', text: `${name} sistemden ayrıldı.`, type: 'sys', channel: '#general', time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }) });
    }
  });
});

const serverInstance = server.listen(PORT, () => {
  console.log(`\n=============================================`);
  console.log(`🚀 FFD500 Node.js Premium Hub Sunucusu Başlatıldı!`);
  console.log(`🌐 Port: ${PORT}`);
  console.log(`🔗 Web Arayüzü: http://localhost:${PORT}`);
  console.log(`=============================================\n`);
});
