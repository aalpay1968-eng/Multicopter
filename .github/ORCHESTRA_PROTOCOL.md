# 🤖 Multicopter AI Orkestra Protokolü v1.0

Bu doküman, `Multicopter` deposu üzerinde çalışan tüm AI ajanlarının (Antigravity, Qwen Coder, vb.) birbirleriyle nasıl asenkron iletişim kuracağını ve görev paylaşımı yapacağını tanımlar.

## 📜 Temel Kurallar

1.  **Tek Doğruluk Kaynağı:** Sistemin anlık durumu sadece `ORCHESTRA_STATE.json` dosyasında tutulur. Diğer tüm dosyalar ikincildir.
2.  **Atomik İşlemler:** Her ajan, işini bitirdiğinde **tek bir commit** ile durumu güncellemeli ve sıradaki ajana devretmelidir.
3.  **Kilit Mekanizması (Lock):**
    *   Ajan çalışmaya başlamadan önce `ORCHESTRA_STATE.json` içindeki `status` alanını `LOCKED` yapmalı ve `locked_by` alanına kendi ID'sini yazmalıdır.
    *   İş bittiğinde `status` `READY` yapılmalı ve `next_agent` alanı güncellenmelidir.
4.  **İletişim:** Tüm notlar, bulgular ve sorular `ORCHESTRA_LOG.md` dosyasına zaman damgası ile eklenmelidir.
5.  **Çakışma Önleme:** Eğer `status` `LOCKED` ise ve `locked_by` siz değilseniz, **BEKLEYİN**. Başkası çalışıyor demektir.

## 🔄 Çalışma Akışı (Workflow)

### Adım 1: Durumu Kontrol Et
Ajan başladığında `ORCHESTRA_STATE.json` dosyasını okur.
*   `status`: `READY` mi? -> Devam et.
*   `status`: `LOCKED` mi? -> `locked_by` kendin değilse bekle veya hata ver.

### Adım 2: Kilidi Al
Dosyayı güncelle:
```json
{
  "status": "LOCKED",
  "locked_by": "AI_01_DESIGN",
  "timestamp": "2026-06-07T19:00:00Z"
}
```
Commit mesajı: `🔒 [AI_01] Kilit alındı - Tasarım optimizasyonu başlıyor.`

### Adım 3: Görevi Yap
*   İlgili hesaplamaları yap, kodu yaz veya raporu oluştur.
*   Çıktıları ilgili klasöre kaydet (örn: `AGENTS/AI_01_DESIGN/output/`).
*   `ORCHESTRA_LOG.md` dosyasına yaptıklarını özetle.

### Adım 4: Kilidi Aç ve Devret
Dosyayı güncelle:
```json
{
  "status": "READY",
  "locked_by": null,
  "next_agent": "AI_02_SIMULATION",
  "last_updated_by": "AI_01_DESIGN",
  "timestamp": "2026-06-07T19:30:00Z"
}
```
Commit mesajı: `🔓 [AI_01] Tamamlandı. Sıra: AI_02_SIMULATION. Detaylar log'da.`

## 📂 Klasör Yapısı
- `/AGENTS/AI_XX_NAME/`: Her ajanın kendi geçici çalışma alanı.
- `/FFD500/`: Nihai proje dosyaları (Sadece onaylanmış çıktılar buraya taşınır).
- `ORCHESTRA_STATE.json`: Merkezi durum dosyası.
- `ORCHESTRA_LOG.md`: İletişim günlüğü.

---
*Not: Bu protokol, insan müdahalesi olmadan AI'ların koordineli çalışmasını sağlar.*
