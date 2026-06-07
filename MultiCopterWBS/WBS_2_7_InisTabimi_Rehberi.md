# 🏗️ WBS 2.7 — İNİŞ TAKIMI & MONTAJ NOKTALARI

> **İniş Takımı Geometrisi | Temas Kuvveti | Payload Flanşı | Devrilme Stabilitesi**  
> Raymer §11 | EASA CS-27 §27.473 | MIL-HDBK-516C | KK-10: Devrilme ≥ 30°

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 2.7 |
| **Faz** | AŞAMA 2 — Konfigürasyon & 3D Geometri |
| **Görev** | İniş Takımı & Montaj Noktaları |
| **Girdi** | `cg_result.json` (WBS 2.6) + `geometry.json` (WBS 2.2) + `requirements.json` |
| **LLM Script** | `landing_gear.py` |
| **Çıktı** | `landing_gear.json`: leg_type, n_legs, leg_height_m, track_m, tipover_angle_deg, F_contact_N, payload_flange_z_m |
| **Kabul Kriteri** | KK-10: tipover ≥ 30° \| rotor-zemin ≥ D_rotor×0.3 \| F_contact×1.5 ≤ F_ult (WBS 6.4) \| Pydantic PASS |
| **Sonraki WBS** | WBS 6.4 FEA \| WBS 9.3 İniş Prosedürü \| WBS 12.2 Montaj \| WBS 14.3 Teknik Çizim |
| **Standartlar** | Raymer §11 \| EASA CS-27 §27.473 \| MIL-HDBK-516C §15 \| MIL-A-8862 |

---

## 🔟 5 Adımlı Algoritma

### Adım 1: Tip & Bacak Sayısı Seçimi

| Tip | Bacak | MTOW Aralığı | Devrilme | Not |
|-----|-------|-------------|----------|-----|
| **SKID** | 2 | 0–5 kg | ~25° | Hafif, düz zemin |
| **TRIPOD** | 3 | 5–30 kg | ~35° | Dengeli iniş |
| **QUAD** | 4 | 20–150 kg | ~40–50° | En kararlı |
| **QUAD katlanır** | 4 | 5–50 kg | ~40° | Kompakt taşıma |
| **HEX** | 6 | 50–200 kg | ~50° | Ağır platform |

### Adım 2: Geometri Hesabı

```python
h_leg_min  = D_rotor * 0.30          # rotor-zemin minimum
h_leg      = max(h_leg_min, payload_clearance + 0.05)

# QUAD: track = wheelbase * 0.70
track_min  = 2 * h_CG_ground * tan(30°)   # KK-10 için minimum
track      = max(wheelbase * 0.70, track_min)

rotor_clearance = h_leg   # flat layout (disk hub seviyesinde)
# Kabul: rotor_clearance ≥ D_rotor × 0.30
```

### Adım 3: Dinamik Temas Kuvveti

```python
v_sink       = sqrt(2 × g × h_drop)           # h_drop=0.30 m standart
F_contact    = MTOW×g + MTOW × v_sink² / (2 × stroke)
F_contact_FS = F_contact × 1.5                 # güvenlik faktörü
F_per_leg    = F_contact_FS × 0.60 / n_legs   # asimetrik iniş (%60 en kötü ayağa)
# → WBS 6.4 FEA: F_per_leg ≤ F_ultimate_leg
```

**Zemin tipine göre dinamik kuvvet:**

| Zemin | h_drop | v_sink | stroke | F / (MTOW×g) |
|-------|--------|--------|--------|--------------|
| Beton/Asfalt | 0.30 m | 2.43 m/s | 0.05 m | ~7.0× |
| Çim/Toprak | 0.30 m | 2.43 m/s | 0.08 m | ~4.7× |
| Kar/Kum | 0.30 m | 2.43 m/s | 0.12 m | ~3.5× |
| Serbest düşüş testi | 1.00 m | 4.43 m/s | 0.05 m | ~21× |

### Adım 4: Devrilme Stabilitesi (KK-10)

```python
h_CG_ground     = leg_height + CG_z          # CG'nin yerden yüksekliği
tipover_angle   = arctan( track/2 / h_CG_ground )   [derece]
# KK-10: tipover_angle ≥ 30°

alpha_max       = tipover_angle - 10°         # operasyonel eğim limiti
# Eğimli zemin (10°): tipover_eff = tipover - 10° ≥ 20° (tercih)
```

**Devrilme senaryoları:**

| Konfig. | track | CG_z | Devrilme | KK-10 |
|---------|-------|------|----------|-------|
| QUAD WB×0.70, CG_z=0.05 | geniş | düşük | ~82° | ✅ |
| QUAD WB×0.30, CG_z=0.10 | orta | orta | ~56° | ✅ |
| QUAD WB×0.15, CG_z=0.20 | dar | yüksek | ~21° | ❌ FAIL |

### Adım 5: Payload Montaj Flanşı

```python
payload_flange_z  = -(leg_height * 0.50)    # hub altında
# Kabul: |payload_flange_z| + h_payload < leg_height  (zemine çarpmaz)

payload_mount = {
    'type':        'bolt_circle',
    'bolt_size':   'M6',
    'n_bolts':     4,
    'bolt_circle': 0.060,      # m
    'quick_release': False,
}
# WBS 2.6 payload zarfı: CG kayma ≤ 3 mm (KK-6)
```

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| **KK-10** | tipover_angle | ≥ 30° | track artır; CG_z azalt |
| — | rotor_clearance | ≥ D_rotor×0.30 | h_leg artır |
| WBS 6.4 | F_per_leg × 1.5 | ≤ F_ultimate | Bacak kesitini büyüt |
| KK-6 | payload_CG_kayma | ≤ 3 mm | Flanş konumunu ortala |

---

## 🔗 WBS Bağlantıları

```
cg_result.json (WBS 2.6)  ──┐
geometry.json (WBS 2.2)   ──┤── landing_gear.py ──► landing_gear.json
requirements.json         ──┘          │
                                        ├── WBS 6.4 landing_fea.py
                                        ├── WBS 9.3 landing_procedure.py
                                        ├── WBS 12.2 assembly (payload_mount)
                                        └── WBS 14.3 teknik çizim
```

---

## landing_gear.json Şeması (Pydantic LandingResult)

```python
class LandingResult(BaseModel):
    leg_type:               str
    n_legs:                 int
    leg_height_m:           float    # gt=0
    track_m:                float    # gt=0
    rotor_clearance_m:      float    # ge=0
    rotor_clearance_ok:     bool
    v_sink_ms:              float
    F_contact_N:            float
    F_contact_x15_N:        float    # güvenlik faktörlü
    F_per_leg_N:            float
    tipover_angle_deg:      float    # ≥ 30° (KK-10)
    KK10_pass:              bool
    alpha_max_deg:          float
    track_ok:               bool
    payload_flange_z_m:     float
    payload_mount:          dict
    validation_passed:      bool = True
```

---

*WBS 2.7 İniş Takımı & Montaj Noktaları Detay Rehberi v4.0 — Nisan 2026*  
*5 Adım | KK-10 Devrilme ≥ 30° | Dinamik F_contact | Payload Flanşı | Pydantic LandingResult*
