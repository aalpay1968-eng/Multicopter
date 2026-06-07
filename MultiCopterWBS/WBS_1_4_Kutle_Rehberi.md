# ⚖️ WBS 1.4 — BAŞLANGIÇ KÜTLE BÜTÇESİ (WEIGHT STATEMENT)

> **7 bileşen grubu bazında iteratif kütle bütçesi.**
> Staufenbiel metodolojisi | Raymer §15 | NDARC | CG Zarfı | <%1 kapanış hatası

---
## 📊 7 Bileşen Grubu & Fraksiyon Hedefleri

| Grup | Fraksiyon (CFRP) | Fraksiyon (Al) | Kritik Parametre |
|------|-----------------|-----------------|-----------------|
| **Yapı & Gövde** | 0.18-0.25 | 0.25-0.32 | MS ≥ 1.5 @ 3.5g (KK-6) |
| **Tahrik Sistemi** | 0.10-0.18 | 0.10-0.18 | T/W ≥ 2.0 (KK-1) |
| **Güç Sistemi** | 0.28-0.40 | 0.28-0.40 | t_hover ≥ req×1.2 (KK-3) |
| **Aviyonik & GNC** | 0.02-0.05 | 0.02-0.05 | Dual IMU; BW ≥ 10 Hz (KK-9) |
| **Payload** | ≥ 0.15 | ≥ 0.15 | CG sapma ≤ 3 mm |
| **Diğer/Misc** | 0.015-0.03 | 0.020-0.03 | Göz ardı edilmemeli! |

---
## 🔄 İteratif Kapanış Algoritması

```python
# Staufenbiel iteratif kütle denklemi
MTOW = MTOW_target  # başlangıç
while abs(MTOW_new - MTOW) / MTOW > 0.01:  # %1 tolerans
    m_bat    = E_req / (Wh_per_kg × η_pack)  # P×t / η
    m_struct = f_struct × MTOW                # malzeme bağlı
    MTOW_new = m_struct + m_prop + m_bat + m_avion + m_payload + m_misc
    MTOW = MTOW_new
# Yakınsama: tipik 3-8 iterasyon
```

---
## 📐 Malzeme Seçim Kriteri

| Malzeme | σ_ult (MPa) | ρ (kg/m³) | f_struct tipik | Kullanım |
|---------|------------|-----------|----------------|---------|
| CFRP T700 | 600-800 | 1600 | 0.22-0.28 | CFRP: MS kütle bütçesi |
| Al 6061-T6 | 310 | 2700 | 0.28-0.35 | Al: bütçe kısıtı |
| Al 7075-T6 | 570 | 2800 | 0.25-0.32 | Al yüksek mukavemet |
| Ti 6Al-4V | 950 | 4430 | 0.20-0.25 | Motor montaj kritik |
| PA12/Nylon | 50 | 1100 | 0.35-0.45 | 3D baskı: prototip |
| PLA/ABS (3D) | 40-60 | 1200 | 0.40-0.55 | Yalnızca prototip |

---
*WBS 1.4 Kütle Bütçesi Detay Rehberi v4.0 — Nisan 2026*