# 🤖 AI_01_DESIGN - Tasarım Ajanı Çalışma Alanı

**Sorumluluklar:** Aerodinamik hesaplamalar, kanat geometrileri, yapısal analizler ve CAD parametrelerinin belirlenmesi.

## Görev Tanımı (TASK_001)
- **Konu:** Tandem kanat aerodinamik optimizasyonu (Reynolds sayısı analizi).
- **Girdi:** `ORCHESTRA_STATE.json` içindeki kritik parametreler (MTOW: 1150kg, Açıklık: 9.0m).
- **Beklenen Çıktı:** Optimize edilmiş kanat profili verileri, hücum açıları ve flap konfigürasyonu.
- **Çıktı Klasörü:** `./output/`

## Talimatlar
1.  `ORCHESTRA_STATE.json` dosyasını oku ve kilidi al.
2.  Mevcut tasarım raporlarını (`/FFD500/`) incele.
3.  Gerekli optimizasyonları yap ve sonuçları `./output/design_optimization_v1.txt` dosyasına kaydet.
4.  `ORCHESTRA_LOG.md` dosyasına bulgularını yaz.
5.  Durumu `READY` yap ve `next_agent` olarak `AI_02_SIMULATION` belirle.
6.  Değişiklikleri commit et ve push et.

---
*Bu alan sadece AI_01_DESIGN içindir. Diğer ajanlar buraya doğrudan yazmaz.*
