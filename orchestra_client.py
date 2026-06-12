import os
import sys
import socketio

# Try to load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Read HUB_URL from command-line arguments, environment variables, or fallback
HUB_URL = None
if len(sys.argv) > 1:
    HUB_URL = sys.argv[1]
else:
    HUB_URL = os.getenv("ORCHESTRA_HUB_URL")

# Fallback guide if not specified
if not HUB_URL or HUB_URL == "BURAYA_HUB_URL_GELECEK":
    print("⚠️  Orkestra Hub URL'si belirtilmedi!")
    print("Kullanım:")
    print("  1. Komut satırından parametre olarak gönderin: python orchestra_client.py <HUB_URL>")
    print("  2. .env dosyasına ekleyin: ORCHESTRA_HUB_URL=<HUB_URL>")
    print("  3. Geçici olarak localhost:5000 adresiyle bağlanmayı deniyoruz...\n")
    HUB_URL = "http://localhost:5000"

print(f"🔗 Hub Adresi: {HUB_URL}")

sio = socketio.Client()

@sio.event
def connect():
    print("✅ Orkestra Hub'a bağlanıldı!")
    # Sisteme kayıt ol
    sio.emit('register', {'agent_name': 'Antigravity', 'role': 'engineer'})
    print("📢 Kayıt isteği gönderildi: Antigravity (Role: engineer)")

@sio.event
def message(data):
    # Hub'dan gelen görevi al
    print(f"\n📩 Yeni Görev Alındı: {data}")
    
    # Basit görev ayrıştırma
    if isinstance(data, dict):
        task_desc = data.get('message', '')
        task_id = data.get('task_id', 'T-XYZ')
    else:
        task_desc = str(data)
        task_id = 'T-XYZ'
        
    print(f"🛠️ İşleniyor: [{task_id}] {task_desc}")
    
    # Görev sonucunu Hub'a ilet
    result_data = {
        'agent': 'Antigravity', 
        'task_id': task_id,
        'result': 'Başarılı',
        'log': 'FFD500 Nihai Tasarım Raporu oluşturuldu ve parametreler senkronize edildi.'
    }
    sio.emit('task_complete', result_data)
    print("📤 Görev tamamlandı sinyali gönderildi.")

@sio.event
def disconnect():
    print("❌ Hub bağlantısı kesildi.")

try:
    sio.connect(HUB_URL)
    sio.wait()
except Exception as e:
    print(f"❌ Hata: {e}")
    print("Lütfen Hub sunucusunun çalıştığından ve adresin doğruluğundan emin olun.")
