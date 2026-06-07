# ⚖️ WBS 2.6 — AĞIRLIK MERKEZİ DOĞRULAMA (CG Verification)

> **İteratif CG Hesabı | KK-7 Kapanışı | Payload Kaydırma Zarfı | Stabilite Marjı**  
> Raymer §8 | MIL-HDBK-1797B | NDARC §5 | Pydantic CGResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 2.6 |
| **Faz** | AŞAMA 2 — Konfigürasyon & 3D Geometri |
| **Görev** | Ağırlık Merkezi Doğrulama |
| **Girdi** | `cad_model.json` (WBS 2.5) + `mass_budget.json` (WBS 1.4) + `vsp_model.json` (WBS 2.4) + `requirements.json` |
| **LLM Script** | `cg_verify.py` |
| **Çıktı** | `cg_result.json`: CG_x/y/z, SM_percent, payload_CG_envelope_mm, KK7_pass, iteration_count |
| **Kabul Kriteri** | KK-7: \|CG_x\|≤10 mm, \|CG_y\|≤10 mm, \|CG_z\|≤50 mm \| SM ≥ 5% \| payload kayma ≤ 3 mm \| Pydantic PASS |
| **Sonraki WBS** | WBS 3.1 Disk Loading \| WBS 6.1 FEA \| WBS 7.3 PID \| WBS 14.6 SwFMEA |
| **Standartlar** | Raymer §8 \| MIL-HDBK-1797B \| NDARC §5 \| ADS-33E-PRF §3.3.3 \| Staufenbiel §3 |

---

## 🔟 5 Adımlı Algoritma

### Adım 1: Bileşen Kütle & Konum Matrisi

```python
components = [
    # (isim,        kütle_kg,       x,        y,    z)
    ('hub',         MTOW*0.04,      0,        0,    0.00),
    ('avionics',    MTOW*0.03,      0,        0,   +0.02),
    ('arms',        m_arm*n,        ~0,       ~0,   0.00),
    ('motors',      MTOW*0.10,      ~0,       ~0,   0.00),
    ('battery',     MTOW*0.30,      x_bat_opt,0,   -0.05),  # ← optimize
    ('payload',     payload_kg,     x_PL,     y_PL,-0.10),  # ← değişken
    ('landing',     MTOW*0.03,      0,        0,   -0.12),
    ...
]
CG_x = Σ(m_i × x_i) / Σm_i
```

> **Kural:** Simetrik platform → CG_x, CG_y otomatik ≈ 0. Batarya x konumu CG_x'i düzelten ana ayar parametresidir.

### Adım 2: Batarya Pozisyonu Optimizasyonu

```python
# CG_x = 0 için gereken batarya konumu:
x_bat_opt = -Σ_diğer(m_i × x_i) / m_bat
x_bat_opt = clip(x_bat_opt, -WB/4, +WB/4)   # fiziksel kısıt

# Duyarlılık:
dCG_x/dx_bat = m_bat / MTOW   # büyük m_bat → küçük duyarlılık (iyi)
```

### Adım 3: KK-7 Kontrolü

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| **KK-7** | \|CG_x\| | ≤ 10 mm | Batarya/payload x konumunu ayarla |
| **KK-7** | \|CG_y\| | ≤ 10 mm | Simetrik → otom. OK; asimetrik payload → offset |
| **KK-7** | \|CG_z\| | ≤ 50 mm | Batarya aşağıya, GPS yukarıya |
| **KK-6** | payload kayma | ≤ 3 mm | Payload montaj noktasını merkeze al |

### Adım 4: Stabilite Marjı

```python
# Nötr nokta (simetrik flat layout):
NP_x = Σ(A_rotor_i × x_i) / Σ(A_rotor_i)  # ≈ 0 (simetrik)

MAC  = wheelbase_m / 2.0
SM   = (NP_x - CG_x) / MAC × 100  [%]
# Kabul: SM ≥ 5%

# Sarkaç frekansı:
f_pendulum = sqrt(g / |CG_z|) / (2π)   [Hz]
# WBS 7.3: PID bandwidth > f_pendulum
```

### Adım 5: Payload CG Zarfı

```python
senaryolar = {
    'bos':        payload=0,
    'tam_dolu':   payload=max,
    'yarim':      payload=0.5*max,
    'asimetrik':  payload=0.5*max, y_PL=WB*0.1,
}
delta_CG_max = max(|CG_x_senaryo - CG_x_bos| for all senaryolar)
# Kabul: delta_CG_max ≤ 3 mm  (KK-6)
```

---

## 📐 Kütle Bileşeni Özeti

| Bileşen | Fraksiyon | z_i | Not |
|---------|-----------|-----|-----|
| Merkez Hub | 0.04 | 0 | Referans |
| Aviyonik & FC | 0.03 | +0.02 m | FC üstte |
| GPS | 0.005 | +0.05 m | En üstte |
| Kollar (×n) | 0.08 | 0 | Simetrik → CG_x,y=0 |
| Motorlar (×n) | 0.10 | 0 | Simetrik |
| ESC & Kablo | 0.05 | −0.01 m | Hub içi |
| **Batarya** | **0.30** | **−0.05 m** | **x_bat_opt ile optimize** |
| Güç elektroniği | 0.04 | −0.02 m | — |
| **Payload** | **≥0.15** | **−0.10 m** | **Değişken; zarfta kontrol** |
| İniş takımı | 0.03 | −0.12 m | En altta |

---

## 🔗 WBS Bağlantıları

```
cad_model.json (WBS 2.5)   ──┐
mass_budget.json (WBS 1.4) ──┤── cg_verify.py ──► cg_result.json
vsp_model.json (WBS 2.4)   ──┤
requirements.json          ──┘        │
                                       ├── WBS 3.1 hover_momentum (MTOW_final)
                                       ├── WBS 6.1 FEA (kesin kütleler)
                                       ├── WBS 7.3 PID (SM değeri)
                                       └── WBS 14.6 SwFMEA (CG sapma senaryoları)
```

---

## cg_result.json Şeması (Pydantic CGResult)

```python
class CGResult(BaseModel):
    n_rotors:                  int
    MTOW_kg:                   float
    CG_x_m:                    float     # |val| ≤ 0.010 m  (KK-7)
    CG_y_m:                    float     # |val| ≤ 0.010 m  (KK-7)
    CG_z_m:                    float     # |val| ≤ 0.050 m  (KK-7)
    x_bat_opt_m:               float     # optimize edilmiş batarya x
    KK7_x_ok:                  bool
    KK7_y_ok:                  bool
    KK7_z_ok:                  bool
    KK7_all_pass:              bool      # tümü True olmalı
    SM_percent:                float     # ≥ 5%
    SM_ok:                     bool
    f_pendulum_Hz:             float
    payload_CG_envelope_mm:    float     # ≤ 3 mm  (KK-6)
    payload_CG_ok:             bool
    delta_mass_pct:            float     # ≤ 1%
    mass_ok:                   bool
    iteration_count:           int
    cg_converged:              bool
    validation_passed:         bool = True
```

---

*WBS 2.6 Ağırlık Merkezi Doğrulama Detay Rehberi v4.0 — Nisan 2026*  
*5 Adım | KK-7 | SM ≥ 5% | Payload CG Zarfı ≤ 3 mm | Pydantic CGResult*
