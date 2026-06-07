# 🔀 WBS 1.5 — TRADE-OFF ANALİZİ & KONFİGÜRASYON SEÇİMİ

> **6 alternatif × 12 kriter ağırlıklı Pugh matrisi ile sistematik seçim.**
> AHP ağırlıkları | Eleme filtreleri | Duyarlılık analizi | Pydantic doğrulama

---
## 🚁 6 Alternatif Özeti

| ID | Konfigürasyon | N | OEI | SAIL Max | Payload | En İyi Durum |
|----|---------------|---|-----|---------|---------|-------------|
| **A1** | Quadcopter X | 4 | Yok | SAIL-II | < 3 kg | Hobi, yarış, hafif gözetleme (<2 kg |
| **A2** | Hexacopter X | 6 | N+1 | SAIL-IV | 2-8 kg | Kargo teslimat, tarım, gözetleme (2 |
| **A3** | Octocopter X8 (flat) | 8 | N+2 | SAIL-V | 5-15 kg | Ağır kargo, kentsel teslimat (5-15  |
| **A4** | Y6 Coaxial Tricopter | 6 | Koşullu N+1 | SAIL-III | 1-5 kg | Dar alan, kapalı mekan, kompakt kar |
| **A5** | Octocopter X8 Coaxial | 8 | N+2 | SAIL-VI | > 10 kg | Kritik yük taşıma, insanlı uçak ben |
| **A6** | Hexacopter H-frame | 6 | N+1 | SAIL-IV | 2-8 kg | Profesyonel fotoğrafçılık, lidar ha |

---
## 📊 Ağırlıklı Pugh Sonuçları

| Alternatif | Ham Toplam | Ağırlıklı Skor | Sıra |
|-----------|-----------|---------------|------|
| 🏆 A1 Quadcopter X | +10 | +0.7800 | #1 |
| A6 Hexacopter H-frame | +2 | +0.0900 | #2 |
| A2 Hexacopter X | +2 | +0.0700 | #3 |
| A3 Octocopter X8 (flat) | -2 | -0.2100 | #4 |
| A5 Octocopter X8 Coaxial | -8 | -0.6700 | #5 |
| A4 Y6 Coaxial Tricopter | -10 | -0.8400 | #6 |

---
## 🔑 Karar Ağacı (Hızlı Öneri)

```
IF payload > 8 kg          → A3 (Octo-X8)
IF kompakt + payload < 4   → A4 (Y6-Coax)
IF BVLOS veya SAIL ≥ III:
    IF payload > 5 kg      → A3 (Octo-X8)
    ELSE                   → A2 (Hex-X)  ← en yaygın seçim
IF kamera/harita görevi    → A6 (Hex-H)
IF payload < 2 kg (hafif)  → A1 (Quad-X)
DEFAULT                    → A2 (Hex-X)
→ Pugh matrisi ile doğrula ve gerekçelendir
```

---
*WBS 1.5 Trade-Off Detay Rehberi v4.0 — Nisan 2026 | 6 Alt. | 12 Kriter | Pugh+AHP*