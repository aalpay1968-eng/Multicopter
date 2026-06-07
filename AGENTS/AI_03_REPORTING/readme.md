# 🤖 AI_03_REPORTING - Raporlama Ajanı Çalışma Alanı

**Sorumluluklar:** Nihai teknik raporların hazırlanması, BOM (Malzeme Listesi) doğrulaması ve dokümantasyon.

## Görev Tanımı (TASK_003)
- **Konu:** Nihai üretim raporu ve BOM doğrulaması.
- **Girdi:** `AI_01_DESIGN` (tasarım verileri) ve `AI_02_SIMULATION` (simülasyon sonuçları).
- **Beklenen Çıktı:** Üretim ekibi için nihai `.docx` raporu, güncellenmiş BOM listesi ve risk analizi.
- **Çıktı Klasörü:** `./output/` (Nihai dosyalar `/FFD500/` klasörüne taşınır).

## Talimatlar
1.  `ORCHESTRA_STATE.json` dosyasını kontrol et. `next_agent` sensin ve durum `READY` mi?
2.  Kilidi al (`LOCKED`).
3.  Önceki ajanların çıktılarını (`AGENTS/AI_01_DESIGN/output/` ve `AGENTS/AI_02_SIMULATION/output/`) oku.
4.  Tüm verileri sentezleyerek nihai raporu oluştur (`FireFiterDrone500_Nihai_Rapor_v1.docx`).
5.  Raporu `/FFD500/` klasörüne taşı.
6.  `ORCHESTRA_LOG.md` dosyasına raporu özetle.
7.  Durumu `READY` yap ve `next_agent` olarak `AI_01_DESIGN` (döngü başa döner, iteratif iyileştirme için) veya `null` (proje bitti) belirle.
8.  Değişiklikleri commit et ve push et.

---
*Bu alan sadece AI_03_REPORTING içindir.*
