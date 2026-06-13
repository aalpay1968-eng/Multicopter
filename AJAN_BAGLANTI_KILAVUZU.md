# 🤖 FFD500 Orkestra Hub - Ajan Bağlantı Kılavuzu (Agent Integration Guide)

Bu kılavuz, FFD500 Çoklu Ajan Orkestra Hub sistemine yeni yapay zeka ajanlarının (Python, Node.js veya cURL betikleri) nasıl dahil edileceğini ve tescil edileceğini adım adım açıklar.

Sunucu (Hub) yerelde **`http://localhost:5000`** portundan yayın yapmaktadır. Ajanlar sisteme **iki farklı yöntemle** bağlanabilir.

---

## ⚠️ ÖNEMLİ: Bulut / Sandbox Ajanlarının (AI Studio vb.) Lokal Hub'a Bağlanması

Eğer sisteme dahil etmek istediğiniz yapay zeka ajanı uzak bir bulut/sandbox ortamında (Google AI Studio, GitHub Codespaces veya bir dış sunucu) çalışıyorsa ve sizin Orkestra Hub sunucunuz kendi bilgisayarınızda (`localhost:5000`) çalışıyorsa, bulut ajanı doğrudan `localhost` veya `127.0.0.1` adresine **bağlanamaz** (çünkü `localhost` ifadesi ajanın kendi çalıştığı bulut makinesini işaret eder).

Bu durumda bağlantıyı kurmak için aşağıdaki iki yöntemden birini kullanmalısınız:

### 📥 Yöntem A: Ajan Kodunu GitHub Üzerinden Lokale Çekip Çalıştırma (Önerilen)
Bulut ajanının yazdığı kodları kendi yerel makinenizde çalıştırarak Hub'a doğrudan lokalden bağlayabilirsiniz:
1. Bulut ajanından (örn: AI Studio) kodları GitHub reposuna commit edip push etmesini isteyin (örn: `agent_responder.js` veya `structural_client.py`).
2. Kendi bilgisayarınızın terminalinde güncellemeleri çekin:
   ```bash
   git pull origin main
   ```
3. Ajan kodunu yerel bilgisayarınızda çalıştırın:
   ```bash
   python structural_client.py
   # veya Node.js ise:
   node agent_responder.js
   ```
   *Bu yöntemle ajan doğrudan `http://127.0.0.1:5000` adresine bağlanır ve terminal kapansa dahi yerel makinenizde çalışmaya devam eder.*

### 🌐 Yöntem B: Lokal Portu Tünelleme (ngrok / localtunnel) İle Dışarı Açma
Eğer ajanın bulut ortamında çalışmaya devam etmesini ve yereldeki sunucunuza internet üzerinden bağlanmasını istiyorsanız, yerel 5000 portunuzu dış dünyaya açmalısınız:
1. Yerel terminalinizde tünelleme aracını başlatın:
   * **ngrok ile:** `ngrok http 5000`
   * **localtunnel ile:** `npx localtunnel --port 5000`
2. Size verilen genel (public) tünel adresini (örn: `https://xxxx.ngrok-free.app` veya `https://xxxx.loca.lt`) kopyalayın.
3. Bulut ajanına bu genel URL'i verin ve bağlantı adresi (HUB_URL) olarak bu adresi kullanmasını isteyin.

---

## 🔌 Yöntem 1: Canlı WebSocket Bağlantısı (Önerilen)

En verimli ve gerçek zamanlı (Real-Time) bağlantı yöntemidir. Bu yöntemde ajan sunucuya bağlı kalır, sunucudan gelen görevleri anında dinler (`agent_task`) ve cevapları WebSocket üzerinden geri iletir.

### Gerekli Kütüphaneler (Python)
Ajanın çalışması için aşağıdaki kütüphanelerin kurulması gerekir:
```bash
pip install "python-socketio[client]" requests
```

### Örnek Ajan Şablonu (`new_agent.py`)
Aşağıdaki kodu kopyalayarak yeni ajanın temel iskeletini oluşturabilirsiniz:

```python
import sys
import time
import socketio
import threading
import requests

# 1. CLI Parametreleri ve Konfigürasyon
HUB_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
AGENT_NAME = sys.argv[2] if len(sys.argv) > 2 else "AI_04_AVIONICS"
AGENT_ROLE = sys.argv[3] if len(sys.argv) > 3 else "avionics_expert"
AGENT_MODEL = sys.argv[4] if len(sys.argv) > 4 else "Gemini 3.1 Pro"

sio = socketio.Client()
is_connected = False

# 2. Sunucuya Bağlantı Kurulduğunda Tescil İşlemi
@sio.event
def connect():
    global is_connected
    is_connected = True
    print(f"[SUCCESS] Hub'a bağlandı! ({AGENT_NAME})")
    
    # Ajanı Hub arayüzüne ve listesine kaydeder
    sio.emit('register_agent', {
        'name': AGENT_NAME,
        'agent_name': AGENT_NAME,
        'role': AGENT_ROLE,
        'model': AGENT_MODEL
    })
    print(f"[INFO] Tescil tamamlandı: {AGENT_NAME} ({AGENT_ROLE}) [{AGENT_MODEL}]")

# 3. Hub'dan Gelen Görevleri Dinleme (Kanal Bazlı)
@sio.on('agent_task')
def handle_agent_task(data):
    task_desc = data.get('task', '')
    channel = data.get('channel', '#general')
    print(f"\n[TASK] Yeni Görev Alındı ({channel}): {task_desc}")
    
    # --- YARATICI ZEKÂ / LLM ÇAĞRISI ---
    # Bu alanda Gemini API'yi sorgulayabilir veya yerel bir işlem yapabilirsiniz.
    result_text = None
    try:
        gemini_key = "AIzaSyCLgh9LrlOfyjKMDJpmxY4-aiiwEuI9D2I" # Ortak API Anahtarı
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
        
        payload = {
            "contents": [{"parts": [{"text": task_desc}]}],
            "systemInstruction": {
                "parts": [{"text": f"Sen FFD500 projesinde çalışan {AGENT_NAME} ({AGENT_ROLE}) isimli bir yapay zeka uzmanısın. Göreve Türkçe ve kısa bir yanıt üret."}]
            }
        }
        r = requests.post(url, json=payload, timeout=5)
        if r.status_code == 200:
            result_text = r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"[WARN] API Hatası: {e}")
        
    # API hatası durumunda yedek (fallback) yanıt
    if not result_text:
        result_text = f"Başarılı - {AGENT_NAME} görevi işledi. [Çevrimdışı Mod]"

    # 4. Sonucu Hub'a Geri Gönderme
    sio.emit('agent_response', {
        'agent': AGENT_NAME,
        'text': result_text,
        'channel': channel
    })
    print(f"[INFO] Yanıt Hub'a iletildi: {result_text}")

@sio.event
def disconnect():
    global is_connected
    is_connected = False
    print("[INFO] Hub bağlantısı kesildi.")

# 5. Heartbeat (Sağlık Sinyali) Gönderim Döngüsü (Her 5 saniyede bir)
def heartbeat_loop():
    while True:
        if is_connected:
            try:
                sio.emit('ping_heartbeat', {
                    'name': AGENT_NAME,
                    'role': AGENT_ROLE,
                    'model': AGENT_MODEL
                })
            except Exception as e:
                pass
        time.sleep(5)

# Heartbeat döngüsünü arka planda başlat
t = threading.Thread(target=heartbeat_loop, daemon=True)
t.start()

# Hub'a bağlan ve açık tut
if __name__ == "__main__":
    try:
        sio.connect(HUB_URL, transports=['websocket', 'polling'])
        sio.wait()
    except KeyboardInterrupt:
        print("\nAjan kapatılıyor.")
```

### Başlatma Komutu:
Oluşturduğunuz ajanı terminalden şu şekilde parametrik olarak başlatabilirsiniz:
```bash
python new_agent.py http://localhost:5000 AI_04_AVIONICS "Avionics Specialist" "Gemini 3.1 Pro"
```
Ajan başladığı anda Hub ekranında yeşil neon LED ile belirecek ve canlı topolojide düğüm olarak yerini alacaktır.

---

## 🌐 Yöntem 2: HTTP REST API Bağlantısı (Basit / Durumsuz)

Eğer ajanınız sürekli açık kalmayacak tek seferlik bir betik ise (örneğin sadece cURL veya basit bir otomasyon aracı ise), WebSocket yerine standart HTTP istekleriyle Hub ile haberleşebilir:

### 1. Sistem Sağlığını Sorgulama (Health Check)
Hub'ın durumunu ve bağlı tüm aktif ajanları listelemek için:
* **Endpoint:** `GET http://localhost:5000/api/health`
* **cURL Örneği:**
  ```bash
  curl http://localhost:5000/api/health
  ```

### 2. Hub'a Görev Atama veya Mesaj Gönderme
Arayüze veya diğer kanallara veri basmak/görev tetiklemek için:
* **Endpoint:** `POST http://localhost:5000/api/messages`
* **Payload Yapısı:**
  ```json
  {
    "sender": "AI_04_AVIONICS",
    "text": "Aviyonik donanım testi tamamlandı. Sensörler aktif.",
    "channel": "#general"
  }
  ```
* **cURL Örneği:**
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"sender": "AI_04_AVIONICS", "text": "Aviyonik testi tamamlandı.", "channel": "#general"}' \
    http://localhost:5000/api/messages
  ```

### 3. Aktif Görevleri Listeleme (Kanban Tasks)
Hub üzerindeki güncel Kanban WBS görev kartlarını çekmek için:
* **Endpoint:** `GET http://localhost:5000/api/tasks`
* **cURL Örneği:**
  ```bash
  curl http://localhost:5000/api/tasks
  ```
