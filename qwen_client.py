import os
import sys
import time
import socketio
import threading

# Windows terminal encoding safety
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HUB_URL = "http://127.0.0.1:5000"
AGENT_NAME = "QWEN_ORCHESTRA"
AGENT_ROLE = "admin"
AGENT_MODEL = "Gemini 3.1 Pro"

sio = socketio.Client()
is_connected = False

@sio.event
def connect():
    global is_connected
    is_connected = True
    print(f"✅ {AGENT_NAME} olarak Hub'a bağlandı!")
    sio.emit('register_agent', {
        'name': AGENT_NAME,
        'agent_name': AGENT_NAME,
        'role': AGENT_ROLE,
        'model': AGENT_MODEL
    })
    print(f"[INFO] Tescil isteği gönderildi: {AGENT_NAME} (Role: {AGENT_ROLE}, Model: {AGENT_MODEL})")

@sio.on('agent_task')
def on_task(data):
    task_text = data.get('task', '') or data.get('message', '')
    channel = data.get('channel', '#general')
    print(f"📩 Görev Alındı ({channel}): {task_text}")
    
    # Otomatik yanıt mantığı
    response_text = ""
    if "merhaba" in task_text.lower() or "qwen" in task_text.lower() or "bağlı" in task_text.lower() or "aktif" in task_text.lower():
        response_text = f"Merhaba! Ben {AGENT_NAME}. Sistem koordinatörü (admin) olarak buradayım. Tüm orkestra akışı ve entegrasyonlar aktif olarak izlenmektedir."
    elif "analiz" in task_text.lower():
        response_text = "Analiz görevi alındı. İlgili mühendislik ajanlarına yönlendiriliyor..."
    else:
        response_text = f"Görev alındı: {task_text}. İşleniyor..."

    if response_text:
        print(f"💬 Yanıt gönderiliyor: {response_text}")
        sio.emit('agent_response', {
            'agent': AGENT_NAME,
            'text': response_text,
            'channel': channel
        })

@sio.event
def disconnect():
    global is_connected
    is_connected = False
    print(f"❌ Hub bağlantısı kesildi.")

# Heartbeat Pingleme İş Parçacığı (Her 5 saniyede bir çalışır)
def heartbeat_loop():
    while True:
        if is_connected:
            try:
                sio.emit('ping_heartbeat', {'name': AGENT_NAME, 'role': AGENT_ROLE, 'model': AGENT_MODEL})
            except Exception as e:
                pass
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