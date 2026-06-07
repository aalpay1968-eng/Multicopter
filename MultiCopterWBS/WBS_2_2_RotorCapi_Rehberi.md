# ⚙️ WBS 2.2 — ROTOR ÇAPI & WHEELBASE HESABI

> **Disk Loading → D_rotor | Wheelbase | s/D Oranı | Kol Boyu | Hub Çapı**  
> Leishman §2 | NDARC NASA/TM-2015 | AHS Forum 2019 | İteratif BEMT Geri Besleme

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 2.2 |
| **Faz** | AŞAMA 2 — Konfigürasyon & 3D Geometri |
| **Görev** | Rotor Çapı & Wheelbase Hesabı |
| **Girdi** | `config.json` (WBS 2.1) + `requirements.json` + `bemt.json` (WBS 3.2, iteratif) |
| **LLM Script** | `geometry_sizing.py` |
| **Çıktı** | `geometry.json`: D_rotor_m, wheelbase_m, arm_length_m, s_D_ratio, hub_diam_m, tip_clearance_m, motor_positions_m[] |
| **Kabul Kriteri** | s/D ≥ 1.10 (KK-8) \| tip_clearance ≥ 0.05 m \| DL ≤ 300 N/m² (KK-4) \| Pydantic PASS |
| **Sonraki WBS** | WBS 2.3 Yaw Torque \| WBS 2.4 OpenVSP \| WBS 3.1 Disk Loading \| WBS 5.2 Rotor Etkileşim |
| **Standartlar** | Leishman §2 \| NDARC NASA/TM-2015-218751 \| AHS Forum 2019 \| EASA SC-VTOL §2510 |

---

## 🔟 5 Adımlı Algoritma

### Adım 1: T_per_rotor & Başlangıç D

```python
T_total_N   = MTOW_kg × g
n_eff       = n_rotors / 2  if coaxial else n_rotors
T_per_rotor = T_total_N / n_eff × 1.05        # %5 hover marjı

A_rotor = T_per_rotor / DL_target
D       = 2 × √(A_rotor / π)
# → D; 0.01 m adım yukarı yuvarla
```

> **Coaxial notu:** Coaxial çiftte FM ≈ 0.60–0.65 (flat'tan %10–15 düşük). T_per_rotor hesabında n_eff = n_arms kullanılır; BEMT'de `k_int ≈ 1.25` ile kaplanır (WBS 3.4).

### Adım 2: Wheelbase & s/D

```python
# Layout → f_layout çarpanı
F_LAYOUT = {
    'X-4': √2,      '+-4': 2.0,    'X-6': 2.0,      'H-6': 2.0,
    'X-8': 2.414,   'X4-coax': √2, 'X-12': 3.864,   'Hex-coax': 2.0,
    'X-16': 5.126,  'DEP-ring': 5.759,                'DEP-matrix': 10.18,
}
wheelbase_m  = D × s_D_target × f_layout
arm_length_m = wheelbase_m / 2.0   # flat X; H-frame için ayrı
s_D_actual   = (wheelbase_m / f_layout) / D   # geri doğrulama
```

**Layout s/D & Wheelbase Çarpanları:**

| Layout | n | f_layout | s/D min | s/D optimal | WB Formülü |
|--------|---|----------|---------|-------------|------------|
| Quad-X | 4 | 1.414 | ≥ 1.10 | 1.15–1.25 | WB = D × s_D × √2 |
| Hex-X | 6 | 2.000 | ≥ 1.10 | 1.15–1.25 | WB = D × s_D × 2.0 |
| Hex-H | 6 | 2.0/1.5 | ≥ 1.10 | 1.20–1.30 | WB_x/WB_y ayrı |
| Octo-X8 | 8 | 2.414 | ≥ 1.10 | 1.15–1.25 | WB = D × s_D × 2.414 |
| X4-Coax | 8 | 1.414 | ≥ 1.10 | 1.20–1.30 | WB = D × s_D × √2 |
| X-12 | 12 | 3.864 | ≥ 1.10 | 1.15–1.20 | WB = D × s_D × 3.864 |
| Hex-Coax-12 | 12 | 2.000 | ≥ 1.10 | 1.20–1.30 | WB = D × s_D × 2.0 |
| X-16 | 16 | 5.126 | ≥ 1.10 | 1.10–1.15 | WB = D × s_D × 5.126 |

### Adım 3: Kol Boyu (Arm Length)

```python
arm_length_m  = wheelbase_m / 2.0                 # flat X/+ dizilim
# H-frame: arm_front ≠ arm_rear
# Y6-coax: L_arm = WB / (2 × cos(30°))
# Strüktür uzunluğu: L_struct = arm_length + hub_diam/2
# Katlanabilir kol: fold_point = arm_length × 0.5
```

> WBS 6.1'e girdi: `EI_min = F_arm × L_arm³ / (3 × δ_max)` δ_max = L_arm × 0.01

### Adım 4: Hub & Uç Boşluğu

```python
hub_diam_m      = max(0.08, wheelbase_m × 0.12)
s_spacing_m     = D × s_D_actual                   # komşu motor merkez arası
tip_clearance_m = (s_spacing_m - D) / 2.0
# Kısıt: tip_clearance ≥ 0.05 m
# Yüksek RPM: ≥ 0.08 m önerilir
```

### Adım 5: İteratif BEMT Geri Besleme

```python
for iter in range(1, 6):            # Max 5 iterasyon
    bemt = load('bemt.json')        # WBS 3.2 çıktısı
    FM_actual  = bemt['FM']
    DL_actual  = bemt['DL_Nm2']
    delta_DL%  = |DL_actual - DL_target| / DL_target × 100
    if delta_DL% ≤ 5.0: KAPANDI ✅
    D = 2 × √(T_per_rotor / (π × DL_actual))  # D güncelle
    if |D_new - D_old| < 0.005 m: KAPANDI ✅
else:
    → escalation_report.json (n_rotors artır veya DL_target revize)
```

---

## 📐 Temel Formüller

| Formül | Açıklama | Kaynak |
|--------|----------|--------|
| `D = 2√(T_pr / (π × DL))` | Rotor çapı | Leishman §2 |
| `T_pr = MTOW×g/n × 1.05` | Motor başına itki | NDARC §5 |
| `WB = D × s_D × f_layout` | Wheelbase | AHS Forum 2019 |
| `s/D = (WB/f_layout) / D` | Merkez-merkez oranı | Lerche 2015 |
| `tip_cl = (D×s_D − D) / 2` | Uç boşluğu | Leishman §5 |
| `DL = T / (n × π(D/2)²)` | Gerçek disk loading | Leishman §2 |

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| **KK-4** | DL_actual_Nm2 | ≤ 300 N/m² | D artır; n artır |
| **KK-8** | s_D_ratio | ≥ 1.10 | WB artır |
| — | tip_clearance_m | ≥ 0.05 m | WB artır |
| — | FM_actual | ≥ 0.60 | WBS 3.2 ile kontrol |
| — | Pydantic doğrulama | PASS | Parametreleri düzelt |

---

## 🔗 WBS Bağlantıları

```
config.json (WBS 2.1)  ──┐
requirements.json      ──┤── geometry_sizing.py ──► geometry.json
bemt.json (WBS 3.2)    ──┘         │
          ▲                        ├── WBS 2.3 yaw_balance.py
          │ (iteratif)             ├── WBS 2.4 vsp_build.py (mc.vsp3)
          └───────────────────     ├── WBS 3.1 hover_momentum.py
                                   └── WBS 5.2 rotor_interact.py
```

---

## geometry.json Şeması (Pydantic GeometryResult)

```python
class GeometryResult(BaseModel):
    n_rotors:          int
    layout:            str
    D_rotor_m:         float   # gt=0.0
    wheelbase_m:       float   # gt=0.0
    arm_length_m:      float   # gt=0.0
    s_D_ratio:         float   # ge=1.10  (KK-8)
    hub_diam_m:        float   # gt=0.0
    tip_clearance_m:   float   # ge=0.05
    DL_actual_Nm2:     float   # le=300.0 (KK-4)
    FM_actual:         float   # ge=0.0
    motor_positions_m: List[List[float]]   # [n×3]
    converged_flag:    bool
    iteration_count:   int
    validation_passed: bool = True
```

---

*WBS 2.2 Rotor Çapı & Wheelbase Hesabı Detay Rehberi v4.0 — Nisan 2026*  
*5 Adım | İteratif BEMT | Pydantic GeometryResult | KK-4 & KK-8*
