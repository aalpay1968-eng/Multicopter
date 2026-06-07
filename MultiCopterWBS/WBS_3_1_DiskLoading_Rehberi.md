# 🌀 WBS 3.1 — DİSK LOADING & HOVER MOMENTUM TEORİSİ

> **Actuator Disk | v_induced | P_hover | FM Ön Tahmini | KK-4 DL ≤ 300 N/m²**  
> Leishman §2 | NDARC NASA/TM-2015 | Rankine-Froude | Pydantic HoverResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 3.1 |
| **Faz** | AŞAMA 3 — Aerodinamik & Tahrik Analizi |
| **Görev** | Disk Loading & Hover Momentum Analizi |
| **Girdi** | `cg_result.json` (WBS 2.6) + `geometry.json` (WBS 2.2) + `requirements.json` |
| **LLM Script** | `hover_momentum.py` |
| **Çıktı** | `hover.json`: v_i_ms, P_ideal_W, P_hover_W, FM_estimate, DL_Nm2, T_W_ratio, endurance_hover_min |
| **Kabul Kriteri** | KK-4: DL ≤ 300 N/m² \| KK-1: T/W ≥ 2.0 \| FM ≥ 0.60 \| Pydantic PASS |
| **Sonraki WBS** | WBS 3.2 BEMT \| WBS 3.3 İleri Uçuş \| WBS 3.9 Motor Seçimi \| WBS 4.1 Batarya |
| **Standartlar** | Leishman §2 \| Rankine-Froude Momentum Teorisi \| NDARC §4 \| ISA-1975 |

---

## 🔟 6 Adımlı Algoritma

### Adım 1: ISA Standart Atmosfer

```python
T_h  = 288.15 - 0.0065*h + T_offset    # K
P_h  = 101325 * (T_h/288.15)^(g/R/L)   # Pa
rho  = P_h / (287.05 * T_h)             # kg/m3

# Hızlı yaklaşım: rho ~ 1.225 * exp(-h/8500)
```

**Yükseklik etkisi:**

| Senaryo | İrtifa | rho (kg/m³) | P_hover çarpanı |
|---------|--------|-------------|-----------------|
| Deniz seviyesi ISA | 0 m | 1.225 | 1.000× |
| 1500 m ISA | 1500 m | 1.058 | 1.076× |
| 3000 m ISA | 3000 m | 0.909 | 1.161× |
| DNS + ISA+20°C | 0 m | 1.154 | 1.030× |
| **1500m + ISA+20°C** | 1500 m | **0.995** | **1.110× (en kötü)** |

### Adım 2: Disk Loading & Toplam İtki

```python
A_disk = pi * (D_rotor/2)^2
n_eff  = n_rotors // 2  if coaxial else n_rotors
A_total = n_eff * A_disk

T_total   = MTOW_kg * g
DL        = T_total / A_total          # N/m²
# KK-4: DL ≤ 300 N/m²

T_design  = T_total * 2.0             # T/W=2.0 için motor kapasitesi
# KK-1: T/W ≥ 2.0
```

### Adım 3: İndüklenmiş Hız

```python
v_i_ideal = sqrt( DL / (2*rho) )      # Rankine-Froude

# Coaxial etki:
k_int = 1.20  # (1.16–1.25 arası, Leishman §8)
v_i   = v_i_ideal * sqrt(k_int)       # coaxial için
```

### Adım 4: İdeal Güç

```python
P_ideal = T_total * v_i_ideal          # W
# Alternatif: P_ideal = sqrt(T^3 / (2*rho*A_total))
```

### Adım 5: FM Ön Tahmini & Gerçek Güç

```python
# DL bazlı FM ön tahmini:
FM_est = 0.68  if DL < 100
FM_est = 0.65  if DL < 200
FM_est = 0.62  if DL < 300
FM_est *= 0.88 if coaxial          # coaxial FM cezası

P_hover = P_ideal / FM_est          # W (gerçek hover gücü)
# WBS 3.2 BEMT → gerçek FM hesabı
```

### Adım 6: Sistem Gücü & Dayanım

```python
eta_system  = 0.87                   # ESC × motor × kablo
P_total     = (P_hover + P_avionics + P_payload) / eta_system
t_hover_min = E_bat_usable_Wh / P_total * 60   # dakika
# E_bat_usable = C_bat_Wh * 0.80
```

---

## 📊 Tipik Referans Değerleri

| Sistem | D_rotor | MTOW | DL (N/m²) | FM | P_hover (W) |
|--------|---------|------|-----------|-----|-------------|
| DJI Mini 4 Pro | 0.075 m | 0.25 kg | ~100 | 0.65 | ~22 |
| DJI Matrice 300 | 0.190 m | 9.0 kg | ~150 | 0.65 | ~800 |
| GRIFF 135 (Octo) | 0.600 m | 60 kg | ~150 | 0.65 | ~5200 |
| GRIFF 300 (Coax) | 0.800 m | 135 kg | ~165 | 0.60 | ~16500 |
| Volocopter VoloDrone | 0.750 m | 200 kg | ~235 | 0.62 | ~29000 |

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| **KK-4** | DL_Nm2 | ≤ 300 N/m² | D_rotor artır (WBS 2.2'ye geri) |
| **KK-1** | T/W_ratio | ≥ 2.0 | Motor gücünü artır (WBS 3.9) |
| — | FM_estimate | ≥ 0.60 | Kanat geometrisini iyileştir (WBS 3.2) |
| — | t_hover | ≥ t_mission×1.20 | Batarya kapasitesini artır (WBS 4.1) |

---

## 🔗 WBS Bağlantıları

```
cg_result.json (WBS 2.6)  ──┐
geometry.json (WBS 2.2)   ──┤── hover_momentum.py ──► hover.json
requirements.json         ──┘          │
                                        ├── WBS 3.2 bemt.py (gerçek FM)
                                        ├── WBS 3.3 forward_flight.py
                                        ├── WBS 3.9 motor_select.py
                                        └── WBS 4.1 battery_size.py
```

---

## hover.json Şeması (Pydantic HoverResult)

```python
class HoverResult(BaseModel):
    MTOW_kg:              float
    altitude_m:           float
    rho_kgm3:             float    # gt=0
    n_rotors:             int
    coaxial_flag:         bool
    A_total_m2:           float    # gt=0
    DL_Nm2:               float    # gt=0  → KK-4 ≤ 300
    T_per_rotor_N:        float
    v_i_ms:               float    # gt=0
    k_int:                float    # coaxial etkileşim
    P_ideal_W:            float
    P_hover_W:            float
    FM_estimate:          float    # 0-1
    T_W_ratio:            float    # KK-1 ≥ 2.0
    P_total_W:            float
    endurance_hover_min:  float
    KK1_pass:             bool
    KK4_pass:             bool
    FM_pass:              bool
    validation_passed:    bool = True
```

---

*WBS 3.1 Disk Loading & Hover Momentum Teorisi Detay Rehberi v4.0 — Nisan 2026*  
*6 Adım | Rankine-Froude | ISA Atmosfer | KK-1 T/W ≥ 2.0 | KK-4 DL ≤ 300 N/m² | Pydantic HoverResult*
