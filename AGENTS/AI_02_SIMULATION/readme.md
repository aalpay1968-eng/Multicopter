# 🤖 AI_02_SIMULATION - Simülasyon Ajanı Çalışma Alanı

**Sorumluluklar:** Güç sistemi simülasyonları, termal analizler, uçuş dinamiği ve pil ömrü hesaplamaları.

## Görev Tanımı (TASK_002)
- **Konu:** Hibrit güç sistemi termal simülasyonu ve verimlilik analizi.
- **Girdi:** `AI_01_DESIGN` ajanından gelen optimize edilmiş aerodinamik veriler.
- **Beklenen Çıktı:** Motor/jeneratör sıcaklık haritaları, yakıt tüketim grafiği ve batarya deşarj eğrileri.
- **Çıktı Klasörü:** `./output/`

## Talimatlar
1.  `ORCHESTRA_STATE.json` dosyasını kontrol et. `next_agent` sensin ve durum `READY` mi?
2.  Kilidi al (`LOCKED`).
3.  `AGENTS/AI_01_DESIGN/output/` klasöründeki tasarım verilerini oku.
4.  Simülasyonları çalıştır ve sonuçları `./output/simulation_results_v1.txt` dosyasına kaydet.
5.  `ORCHESTRA_LOG.md` dosyasına bulgularını yaz (Örn: "Jeneratör %85 verimle çalışıyor, soğutma yeterli").
6.  Durumu `READY` yap ve `next_agent` olarak `AI_03_REPORTING` belirle.
7.  Değişiklikleri commit et ve push et.

---
*Bu alan sadece AI_02_SIMULATION içindir.*
