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

// Ajan görev takip yardımcı fonksiyonları
function setAgentTask(agentName, taskText) {
  for (const [sid, info] of Object.entries(active_agents)) {
    if (info.name === agentName) {
      info.currentTask = taskText;
      break;
    }
  }
}

function clearAgentTask(agentName) {
  for (const [sid, info] of Object.entries(active_agents)) {
    if (info.name === agentName) {
      info.currentTask = null;
      break;
    }
  }
}


// Çoklu proje yapılandırması
let currentProject = 'FireFiterDrone500';
const PROJECTS_DIR = path.join(__dirname, 'PROJECTS');
if (!fs.existsSync(PROJECTS_DIR)) {
  fs.mkdirSync(PROJECTS_DIR, { recursive: true });
}

// Varsayılan projeyi hazırla ve kök dosyalarını yedekle
const defaultProjDir = path.join(PROJECTS_DIR, 'FireFiterDrone500');
if (!fs.existsSync(defaultProjDir)) {
  fs.mkdirSync(defaultProjDir, { recursive: true });
  const rootState = path.join(__dirname, 'ORCHESTRA_STATE.json');
  const rootLog = path.join(__dirname, 'ORCHESTRA_LOG.md');
  const docState = path.join(__dirname, 'FFD500', 'docs', 'ORCHESTRA_STATE.json');
  const docLog = path.join(__dirname, 'FFD500', 'docs', 'ORCHESTRA_LOG.md');
  
  const srcState = fs.existsSync(docState) ? docState : (fs.existsSync(rootState) ? rootState : null);
  const srcLog = fs.existsSync(docLog) ? docLog : (fs.existsSync(rootLog) ? rootLog : null);
  
  if (srcState) fs.copyFileSync(srcState, path.join(defaultProjDir, 'ORCHESTRA_STATE.json'));
  if (srcLog) fs.copyFileSync(srcLog, path.join(defaultProjDir, 'ORCHESTRA_LOG.md'));
}

// Dosya yolları bulucu
function getPaths() {
  const projState = path.join(PROJECTS_DIR, currentProject, 'ORCHESTRA_STATE.json');
  const projLog = path.join(PROJECTS_DIR, currentProject, 'ORCHESTRA_LOG.md');
  return {
    statePath: projState,
    logPath: projLog
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
      } else if (bodyLower.includes('yapısal') || bodyLower.includes('structural') || bodyLower.includes('fea')) {
        channel = '#structural';
      } else if (bodyLower.includes('kalite') || bodyLower.includes('denet') || bodyLower.includes('qa') || bodyLower.includes('audit')) {
        channel = '#qa';
      }
      
      let type = 'sys';
      if (sender.toLowerCase().includes('yönetici') || sender.toLowerCase().includes('admin') || sender.toLowerCase().includes('chief')) {
        type = 'admin';
      } else if (sender.toLowerCase().includes('antigravity') || sender.toLowerCase().includes('agent') || sender.toLowerCase().includes('bot') || sender.toLowerCase().includes('specialist') || sender.toLowerCase().includes('auditor') || sender.toLowerCase().startsWith('ai_') || sender.toLowerCase().startsWith('qa_')) {
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
    
    // Write to project folder
    const jsonStr = JSON.stringify(state, null, 2);
    fs.writeFileSync(statePath, jsonStr, 'utf8');
    
    // Write to root for backward compatibility with clients
    const rootState = path.join(__dirname, 'ORCHESTRA_STATE.json');
    fs.writeFileSync(rootState, jsonStr, 'utf8');
    
    // Write to docState if needed
    if (currentProject === 'FireFiterDrone500') {
      const docState = path.join(__dirname, 'FFD500', 'docs', 'ORCHESTRA_STATE.json');
      if (fs.existsSync(path.dirname(docState))) {
        fs.writeFileSync(docState, jsonStr, 'utf8');
      }
    }
    console.log(`[FILE] State dosyaları güncellendi: ${statePath}`);
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
    
    const updatedContent = header + newEntry + body;
    fs.writeFileSync(logPath, updatedContent, 'utf8');
    
    // Write to root for backward compatibility with clients
    const rootLog = path.join(__dirname, 'ORCHESTRA_LOG.md');
    fs.writeFileSync(rootLog, updatedContent, 'utf8');
    
    // Write to docLog if needed
    if (currentProject === 'FireFiterDrone500') {
      const docLog = path.join(__dirname, 'FFD500', 'docs', 'ORCHESTRA_LOG.md');
      if (fs.existsSync(path.dirname(docLog))) {
        fs.writeFileSync(docLog, updatedContent, 'utf8');
      }
    }
    console.log(`[FILE] Log dosyaları güncellendi: ${logPath}`);
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

// Ajan pingleme ve sağlık takip döngüsü (3 saniyede bir çalışır)
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
    } else {
      let targetStatus = 'IDLE';
      if (agent.currentTask) {
        targetStatus = agent.name === 'QA_AUDITOR' ? 'AUDITING' : 'RUNNING';
      }
      if (oldStatus !== targetStatus) {
        agent.status = targetStatus;
        changed = true;
      }
    }
  }
  
  if (changed) {
    io.emit('update_agents', active_agents);
  }
}, 3000);

// --- REST API ENDPOINTS ---
app.get('/api/projects', (req, res) => {
  try {
    const dirs = fs.readdirSync(PROJECTS_DIR, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);
    res.json({ projects: dirs, active: currentProject });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/projects', (req, res) => {
  const { name, mtow, payload, span, flight_time } = req.body;
  if (!name) {
    return res.status(400).json({ error: "Proje ismi zorunludur." });
  }
  const cleanName = name.replace(/[^a-zA-Z0-9_-]/g, "");
  const projDir = path.join(PROJECTS_DIR, cleanName);
  
  if (fs.existsSync(projDir)) {
    return res.status(400).json({ error: "Bu isimde bir proje zaten mevcut." });
  }
  
  try {
    fs.mkdirSync(projDir, { recursive: true });
    
    const defaultState = {
      project: cleanName,
      version: "1.0.0",
      last_updated: new Date().toISOString(),
      orchestra_chief: "ANTIGRAVITY",
      system_status: "READY",
      locked_by: null,
      current_task: null,
      last_updated_by: "Conductor",
      current_agent: null,
      next_agent: "AI_01_DESIGN",
      pending_tasks: [
        {
          id: "TASK_001",
          description: "Tasarım optimizasyonu ve aerodinamik analizler",
          status: "PENDING",
          assigned_to: "AI_01_DESIGN"
        },
        {
          id: "TASK_002",
          description: "Güç sistemi termal simülasyonu",
          status: "PENDING",
          assigned_to: "AI_02_SIMULATION"
        },
        {
          id: "TASK_003",
          description: "Nihai raporlama ve BOM kontrolü",
          status: "PENDING",
          assigned_to: "AI_03_REPORTING"
        }
      ],
      critical_parameters: {
        MTOW_kg: parseFloat(mtow) || 1000,
        payload_kg: parseFloat(payload) || 300,
        wing_span_m: parseFloat(span) || 8.0,
        flight_time_min: parseFloat(flight_time) || 90
      }
    };
    
    const defaultLog = `# 📜 Orkestra İletişim Günlüğü (Orchestra Log) - ${cleanName}\n\nBu dosya, tüm AI ajanlarının birbirine bıraktığı notları, uyarıları ve görev özetlerini içerir. **Ters kronolojik sıra** ile doldurulmalıdır.\n\n---\n\n## [${new Date().toISOString().replace('T', ' ').substring(0, 19)}] - SISTEM (Proje Başlatıldı)\n**Görev:** Yeni proje oluşturuldu.\n**Açıklama:**\n- ${cleanName} projesi sisteme başarıyla eklendi ve başlatıldı.\n\n**Sonraki Eylem:**\n- Ajanların görevleri işlemek üzere hazır olması bekleniyor.\n\n---`;
    
    fs.writeFileSync(path.join(projDir, 'ORCHESTRA_STATE.json'), JSON.stringify(defaultState, null, 2), 'utf8');
    fs.writeFileSync(path.join(projDir, 'ORCHESTRA_LOG.md'), defaultLog, 'utf8');
    
    res.json({ status: "success", project: cleanName });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/projects/switch', (req, res) => {
  const { name } = req.body;
  if (!name) {
    return res.status(400).json({ error: "Proje ismi belirtilmedi." });
  }
  const cleanName = name.replace(/[^a-zA-Z0-9_-]/g, "");
  const projDir = path.join(PROJECTS_DIR, cleanName);
  
  if (!fs.existsSync(projDir)) {
    return res.status(404).json({ error: "Proje bulunamadı." });
  }
  
  try {
    const { statePath, logPath } = getPaths();
    const rootState = path.join(__dirname, 'ORCHESTRA_STATE.json');
    const rootLog = path.join(__dirname, 'ORCHESTRA_LOG.md');
    
    if (fs.existsSync(rootState)) {
      fs.copyFileSync(rootState, statePath);
    }
    if (fs.existsSync(rootLog)) {
      fs.copyFileSync(rootLog, logPath);
    }
    
    currentProject = cleanName;
    
    const newPaths = getPaths();
    if (fs.existsSync(newPaths.statePath)) {
      fs.copyFileSync(newPaths.statePath, rootState);
    }
    if (fs.existsSync(newPaths.logPath)) {
      fs.copyFileSync(newPaths.logPath, rootLog);
    }
    
    console.log(`[PROJECT_SWITCH] Aktif proje değiştirildi: ${currentProject}`);
    
    io.emit('project_switched', { project: currentProject });
    io.emit('load_history', loadLogHistory());
    io.emit('load_tasks', loadStateTasks());
    
    res.json({ status: "success", active: currentProject });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/projects/delete', (req, res) => {
  const { name } = req.body;
  if (!name) {
    return res.status(400).json({ error: "Proje ismi belirtilmedi." });
  }
  const cleanName = name.replace(/[^a-zA-Z0-9_-]/g, "");
  if (cleanName === 'FireFiterDrone500') {
    return res.status(400).json({ error: "Varsayılan proje silinemez." });
  }
  const projDir = path.join(PROJECTS_DIR, cleanName);
  
  if (!fs.existsSync(projDir)) {
    return res.status(404).json({ error: "Proje bulunamadı." });
  }
  
  try {
    fs.rmSync(projDir, { recursive: true, force: true });
    console.log(`[PROJECT_DELETE] Proje silindi: ${cleanName}`);
    
    let activeProj = currentProject;
    if (currentProject === cleanName) {
      currentProject = 'FireFiterDrone500';
      activeProj = 'FireFiterDrone500';
      
      const rootState = path.join(__dirname, 'ORCHESTRA_STATE.json');
      const rootLog = path.join(__dirname, 'ORCHESTRA_LOG.md');
      const newPaths = getPaths();
      
      if (fs.existsSync(newPaths.statePath)) {
        fs.copyFileSync(newPaths.statePath, rootState);
      }
      if (fs.existsSync(newPaths.logPath)) {
        fs.copyFileSync(newPaths.logPath, rootLog);
      }
      
      io.emit('project_switched', { project: currentProject });
      io.emit('load_history', loadLogHistory());
      io.emit('load_tasks', loadStateTasks());
    }
    
    res.json({ status: "success", deleted: cleanName, active: activeProj });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

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
    clearAgentTask(sender);
    io.emit('update_agents', active_agents);
    appendToLogFile(`${sender} (REST API Cevabı)`, 'Ajan API üzerinden yanıt gönderdi.', `- Bulgular: ${text}`, '- Sistem IDLE.');
  } else {
    if (ch === '#general') {
      updateStateFile(text, 'LOCKED', 'Ajanlar');
      for (const sid of Object.keys(active_agents)) {
        active_agents[sid].currentTask = text;
      }
      io.emit('update_agents', active_agents);
      appendToLogFile(`Yönetici (REST API - #general)`, 'Yönetici API üzerinden genel komut gönderdi.', `- Komut: ${text}`, `- Tüm ajanların çalışması bekleniyor.`);
      io.emit('agent_task', { task: text, from: 'Yönetici', channel: '#general' });
    } else {
      // Kanal ismine göre ajanı belirle
      let assignee = 'AI_01_DESIGN';
      if (ch === '#simulation') assignee = 'AI_02_SIMULATION';
      else if (ch === '#reporting') assignee = 'AI_03_REPORTING';
      else if (ch === '#structural') assignee = 'AI_STRUCTURAL_SPECIALIST';
      else if (ch === '#qa') assignee = 'QA_AUDITOR';
      
      updateStateFile(text, 'LOCKED', assignee);
      setAgentTask(assignee, text);
      io.emit('update_agents', active_agents);
      appendToLogFile(`Yönetici (REST API - ${ch})`, 'Yönetici API üzerinden komut gönderdi.', `- Komut: ${text}`, `- ${assignee} ajanının çalışması bekleniyor.`);
      
      // Ajanı WebSocket ile tetikle!
      emitTaskToAgent(assignee, text, ch);
    }
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
    const model = data.model || 'Gemini 3.1 Pro';
    console.log(`[REGISTER] Ajan Kayıt: ${name} (${role}) [Model: ${model}] - ID: ${socket.id}`);
    
    const currentTask = active_agents[socket.id] ? active_agents[socket.id].currentTask || null : null;
    const initialStatus = currentTask ? (name === 'QA_AUDITOR' ? 'AUDITING' : 'RUNNING') : 'IDLE';
    
    active_agents[socket.id] = {
      name: name,
      role: role,
      model: model,
      status: initialStatus,
      lastSeen: Date.now(),
      time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
      currentTask: currentTask
    };
    
    io.emit('update_agents', active_agents);
    io.emit('broadcast_msg', { sender: 'Sistem', text: `${name} (${role}) sisteme katıldı. [Model: ${model}]`, type: 'sys', channel: '#general', time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }) });
  });

  // Periyodik Heartbeat Pinglemesi (ping_heartbeat)
  socket.on('ping_heartbeat', (data) => {
    const name = data.name || 'Unknown';
    const model = data.model || 'Gemini 3.1 Pro';
    const currentTask = data.currentTask !== undefined ? data.currentTask : null;
    
    const targetStatus = currentTask ? (name === 'QA_AUDITOR' ? 'AUDITING' : 'RUNNING') : 'IDLE';
    
    let changed = false;
    if (active_agents[socket.id]) {
      active_agents[socket.id].lastSeen = Date.now();
      if (active_agents[socket.id].status !== targetStatus) {
        active_agents[socket.id].status = targetStatus;
        changed = true;
      }
      if (data.model && active_agents[socket.id].model !== data.model) {
        active_agents[socket.id].model = data.model;
        changed = true;
      }
      if (active_agents[socket.id].currentTask !== currentTask) {
        active_agents[socket.id].currentTask = currentTask;
        changed = true;
      }
    } else {
      // Yeniden tescil et
      active_agents[socket.id] = {
        name: name,
        role: data.role || 'guest',
        model: model,
        status: targetStatus,
        lastSeen: Date.now(),
        time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
        currentTask: currentTask
      };
      changed = true;
    }
    
    if (changed) {
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

    // Ajanın görevini set et
    setAgentTask(assignee, text);
    io.emit('update_agents', active_agents);

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

    // Tüm ajanların görevini set et
    for (const sid of Object.keys(active_agents)) {
      active_agents[sid].currentTask = txt;
    }
    io.emit('update_agents', active_agents);
    
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
    
    // Ajanın görevini temizle
    clearAgentTask(name);
    io.emit('update_agents', active_agents);

    if (name === 'QA_AUDITOR') {
      appendToLogFile(
        `${name} (Kalite Denetimi)`,
        'Kalite denetim raporu yayınlandı.',
        `- Detaylar: ${txt}`,
        '- Sistem durumu korunuyor.'
      );
      return;
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
