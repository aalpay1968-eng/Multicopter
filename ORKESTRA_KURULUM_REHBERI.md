# 🚁 Multicopter Projesi - AI Orkestra Kurulum Rehberi

Bu doküman, "FireFiterDrone500" ve gelecekteki projeler için birden fazla AI ajanının (Orkestra Mantığı) `Multicopter` deposuna güvenli ve koordineli bir şekilde bağlanmasını sağlar.

## ⚠️ Güvenlik Uyarısı
**ASLA** gerçek `Private Key` (Özel Anahtar), `Passphrase` (Şifre) veya `Token` bilgilerinizi bu Markdown dosyasına veya kod içerisine doğrudan yazmayın. Bu bilgiler sadece yerel `.env` dosyanızda veya sistem ortam değişkenlerinde saklanmalıdır.

## 🛠️ Kurulum Adımları

### 1. Kimlik Bilgilerini Hazırlama
Her AI ajanı için benzersiz bir SSH anahtar çifti veya GitHub Personal Access Token (PAT) oluşturulmalıdır.

#### Seçenek A: SSH Anahtarı (Önerilen)
1. Terminalde şu komutu çalıştırın:
   ```bash
   ssh-keygen -t ed25519 -C "ai-agent-{AGENT_ID}@multicopter.local"
   ```
2. Oluşan özel anahtarı (`id_ed25519`) bir metin editörü ile açın ve tüm içeriğini kopyalayın.
3. Eğer şifre belirlediyseniz, bu şifreyi not edin.

#### Seçenek B: Personal Access Token (PAT)
1. GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic) yolunu izleyin.
2. `repo` kapsamına (scope) sahip yeni bir token oluşturun.

### 2. Yapılandırma Dosyasını Oluşturma
1. Proje kök dizinindeki `.env.example` dosyasını kopyalayın ve adını `.env` yapın.
   ```bash
   cp .env.example .env
   ```
2. `.env` dosyasını açın ve ilgili alanları doldurun:
   - `GITHUB_SSH_PRIVATE_KEY`: Kopyaladığınız özel anahtarı tek satırda `\n` karakterlerini koruyarak yapıştırın.
   - `GITHUB_SSH_PASSPHRASE`: Anahtar şifreliyse şifreyi girin, değilse boş bırakın.
   - `AGENT_ID`: Ajanınıza özel bir kimlik verin (örn: `aerodynamics_bot`).

### 3. Bağlantı ve Çalışma Akışı
AI ajanı çalıştırıldığında şu adımları otomatik olarak izlemelidir:
1. **.env Yüklemesi**: Gizli bilgileri ortam değişkenlerinden oku.
2. **Depoyu Klonla/Güncelle**: `REPO_URL_SSH` adresini kullanarak depoyu çek.
3. **Branch Yönetimi**:
   - `main` branch'inden güncel değişiklikleri al.
   - Kendi görevi için yeni bir branch oluştur: `agent/{AGENT_ID}/{TARIH}_{GOREV}`.
4. **İşlem Yap**: Tasarım, simülasyon veya raporlama işlemlerini gerçekleştir.
5. **Commit & Push**: Değişiklikleri kendi branch'ine gönder.
6. **Pull Request (PR)**: GitHub API üzerinden `main` branch'ine bir PR aç ve açıklama kısmına yapılan işlemleri özetle.

## 🤖 Örnek Python Entegrasyonu (GitPython)
```python
import os
from git import Repo, Git
from dotenv import load_dotenv

load_dotenv()

ssh_key = os.getenv("GITHUB_SSH_PRIVATE_KEY").replace("\\n", "\n")
passphrase = os.getenv("GITHUB_SSH_PASSPHRASE")
agent_id = os.getenv("AGENT_ID")

# Geçici SSH anahtar dosyası oluştur (Güvenli bellek yönetimi önerilir)
with open("temp_key", "w") as f:
    f.write(ssh_key)
os.chmod("temp_key", 0o600)

git_ssh_cmd = f"ssh -i temp_key -o StrictHostKeyChecking=no"
if passphrase:
    # Passphrase handling requires ssh-agent or custom wrapper
    pass 

repo = Repo.clone_from("git@github.com:aalpay1968-eng/Multicopter.git", "./multicopter_work", env={"GIT_SSH_COMMAND": git_ssh_cmd})
# ... İşlemler ...
```

## 📂 Klasör Yapısı
- `/FFD500/`: FireFiterDrone500 projesi dosyaları.
- `/agents/{AGENT_ID}/`: Her ajanın geçici çalışma alanları (opsiyonel).
- `/reports/`: Oluşturulan tasarım raporları.

---
*Bu doküman Multicopter Projesi Orkestra Sistemi v1.0 için hazırlanmıştır.*
