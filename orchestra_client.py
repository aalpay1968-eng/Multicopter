import os
import sys
import time
import socketio
import threading

# Windows terminal encoding safety
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Dynamic CLI parameters
HUB_URL = "http://localhost:5000"
AGENT_NAME = "Antigravity"
AGENT_ROLE = "engineer"

if len(sys.argv) > 1:
    HUB_URL = sys.argv[1]
if len(sys.argv) > 2:
    AGENT_NAME = sys.argv[2]
if len(sys.argv) > 3:
    AGENT_ROLE = sys.argv[3]
else:
    # Fallback to env or defaults
    env_url = os.getenv("ORCHESTRA_HUB_URL")
    if env_url:
        HUB_URL = env_url

print(f"[INFO] Hub Adresi: {HUB_URL}")
print(f"[INFO] Ajan Kimliği: {AGENT_NAME} (Rol: {AGENT_ROLE})")

sio = socketio.Client()
is_connected = False

@sio.event
def connect():
    global is_connected
    is_connected = True
    print(f"[SUCCESS] Orkestra Hub'a bağlandı! ({AGENT_NAME})")
    # Node.js Hub için ajan kayıt
    sio.emit('register_agent', {'name': AGENT_NAME, 'role': AGENT_ROLE})
    print(f"[INFO] Tescil isteği gönderildi: {AGENT_NAME} (Role: {AGENT_ROLE})")

@sio.on('agent_task')
def handle_agent_task(data):
    # Hub'dan gelen görevi al
    task_desc = data.get('task', '')
    sender = data.get('from', 'Yönetici')
    channel = data.get('channel', '#general')
    
    # Sadece doğrudan bu ajana atanmış veya broadcast görevleri al
    print(f"\n[TASK] Yeni Görev Alındı (Kanal: {channel}): {task_desc}")
    print(f"[PROCESS] {AGENT_NAME} görevi işliyor...")
    
    # Gerçekçi işlem gecikmesi taklidi
    time.sleep(2)
    
    # Görev sonucunu Hub'a ilet
    result_text = f"Başarılı - {AGENT_NAME} görevi tamamladı. Rapor güncellendi."
    result_data = {
        'agent': AGENT_NAME, 
        'text': result_text,
        'channel': channel
    }
    sio.emit('agent_response', result_data)
    print(f"[INFO] Yanıt gönderildi: {result_text}")

@sio.event
def disconnect():
    global is_connected
    is_connected = False
    print("[INFO] Hub bağlantısı kesildi.")

# Heartbeat Pingleme İş Parçacığı (Her 5 saniyede bir çalışır)
def heartbeat_loop():
    while True:
        if is_connected:
            try:
                sio.emit('ping_heartbeat', {'name': AGENT_NAME, 'role': AGENT_ROLE})
            except Exception as e:
                print(f"[WARN] Heartbeat hatası: {e}")
        time.sleep(5)

# Heartbeat thread'ini daemon olarak başlat
t = threading.Thread(target=heartbeat_loop, daemon=True)
t.start()

# Otomatik yeniden bağlanma döngüsü
while True:
    try:
        print(f"[INFO] {HUB_URL} adresine bağlanmaya çalışılıyor...")
        sio.connect(HUB_URL, transports=['websocket', 'polling'])
        sio.wait()
    except KeyboardInterrupt:
        print("[INFO] İstemci manuel olarak sonlandırıldı.")
        break
    except Exception as e:
        print(f"[ERROR] Bağlantı Hatası: {e}")
        print("[INFO] 10 saniye sonra tekrar bağlanmayı deneyecek...\n")
        time.sleep(10)
