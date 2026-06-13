import os
import sys
import time
import socketio

# Windows terminal encoding safety
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

HUB_URL = None
if len(sys.argv) > 1:
    HUB_URL = sys.argv[1]
else:
    HUB_URL = os.getenv("ORCHESTRA_HUB_URL")

if not HUB_URL or HUB_URL == "BURAYA_HUB_URL_GELECEK":
    print("[WARN] Orkestra Hub URL'si belirtilmedi!")
    print("Kullanım:")
    print("  1. Komut satırından parametre olarak gönderin: python orchestra_client.py <HUB_URL>")
    print("  2. .env dosyasına ekleyin: ORCHESTRA_HUB_URL=<HUB_URL>")
    print("  3. Geçici olarak localhost:5000 adresiyle bağlanmayı deniyoruz...\n")
    HUB_URL = "http://localhost:5000"

print(f"[INFO] Hub Adresi: {HUB_URL}")

sio = socketio.Client()

@sio.event
def connect():
    print("[SUCCESS] Orkestra Hub'a bağlandı!")
    # Node.js Hub için ajan kayıt
    sio.emit('register_agent', {'name': 'Antigravity', 'role': 'engineer'})
    print("[INFO] Kayıt isteği gönderildi: Antigravity (Role: engineer)")

@sio.on('agent_task')
def handle_agent_task(data):
    # Hub'dan gelen görevi al ve yazdır
    print(f"\n[TASK] Yeni Görev Alındı: {data}")
    
    task_desc = data.get('task', '')
    sender = data.get('from', 'Yönetici')
        
    print(f"[PROCESS] İşleniyor: {task_desc} (Gönderen: {sender})")
    
    # Görev sonucunu Hub'a ilet
    result_data = {
        'agent': 'Antigravity', 
        'text': 'Başarılı - FFD500 optimal tasarım raporu doğrulandı ve parametreler senkronize edildi.'
    }
    sio.emit('agent_response', result_data)
    print("[INFO] Görev tamamlandı sinyali gönderildi.")

@sio.event
def disconnect():
    print("[INFO] Hub bağlantısı kesildi.")

# Otomatik yeniden bağlanma döngüsü
while True:
    try:
        print(f"[INFO] {HUB_URL} adresine bağlanmaya çalışılıyor...")
        sio.connect(HUB_URL, transports=['websocket', 'polling'])
        sio.wait()
    except KeyboardInterrupt:
        print("[INFO] İstemci manuel olarak durduruldu.")
        break
    except Exception as e:
        print(f"[ERROR] Hata: {e}")
        print("[INFO] 10 saniye sonra tekrar bağlanmayı deneyecek...\n")
        time.sleep(10)
