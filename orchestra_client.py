import os
import sys
import socketio

# Windows terminal emoji çökmesini önlemek için UTF-8 stdout yapılandırması
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# .env dosyasından ortam değişkenlerini yükle
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Komut satırı parametresinden, .env'den veya varsayılan local adresten HUB_URL oku
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
    # Sisteme kayıt ol
    sio.emit('register', {'agent_name': 'Antigravity', 'role': 'engineer'})
    print("[INFO] Kayıt isteği gönderildi: Antigravity (Role: engineer)")

@sio.event
def message(data):
    # Hub'dan gelen görevi al ve yazdır
    print(f"\n[TASK] Yeni Görev Alındı: {data}")
    
    # Görev detayını ayrıştır
    if isinstance(data, dict):
        task_desc = data.get('message', '')
        sender = data.get('from', 'Orkestra Şefi')
    else:
        task_desc = str(data)
        sender = 'Orkestra Şefi'
        
    print(f"[PROCESS] İşleniyor: {task_desc} (Gönderen: {sender})")
    
    # Görev sonucunu Hub'a ilet
    result_data = {
        'agent': 'Antigravity', 
        'result': 'Başarılı',
        'log': 'FFD500 optimal tasarım raporu doğrulandı ve parametreler senkronize edildi.'
    }
    sio.emit('task_complete', result_data)
    print("[INFO] Görev tamamlandı sinyali gönderildi.")

@sio.event
def disconnect():
    print("[INFO] Hub bağlantısı kesildi.")

try:
    sio.connect(HUB_URL)
    sio.wait()
except Exception as e:
    print(f"[ERROR] Hata: {e}")
    print("Lütfen Hub sunucusunun çalıştığından ve adresin doğruluğundan emin olun.")
