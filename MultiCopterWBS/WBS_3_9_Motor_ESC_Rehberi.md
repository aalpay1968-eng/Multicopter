# 🔋 WBS 3.9 — MOTOR & ESC SEÇİMİ

> **kV Doğrulama | P_motor_max | I_max | Sıcaklık | Thrust Zinciri | KK-1 & KK-2**  
> T-Motor / KDE / Sunnysky DB | MIL-HDBK-217F | Pydantic MotorESCResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 3.9 |
| **Faz** | AŞAMA 3 — İtki Sistemi & BEMT Analizi |
| **Görev** | Motor & ESC Seçimi + İtki Zinciri Doğrulama |
| **Girdi** | `prop_match.json` (WBS 3.5) + `bemt.json` (WBS 3.2) + `phase_3_aero.json` (WBS 3.8) |
| **LLM Script** | `motor_select.py` |
| **Çıktı** | `motor_esc.json`: motor_model, kV_actual, P_max_W, I_max_A, eta_motor, T_rise_C, ESC_model, thrust_chain_ok |
| **Kabul Kriteri** | KK-1: T/W ≥ 2.0 \| KK-2: T/W_OEI ≥ 1.0 \| KK-12: T_motor ≤ T_max \| I_peak ≤ I_ESC \| Pydantic PASS |
| **Sonraki WBS** | WBS 4.1 Batarya (I_bat_total) \| WBS 6.5 Motor Montaj FEA \| WBS 12.1 BOM |
| **Standartlar** | T-Motor Katalog 2024 \| KDE Direct \| IEC 60034-1 \| EASA SC-VTOL §2525 |

---

## 🔟 6 Adımlı Algoritma

### Adım 1: kV & Motor Seçimi

```python
kV_target  = RPM_hover / V_bat_nominal        # prop_match.json'dan
P_req      = P_hover / n_rotors × 2.0         # T/W=2.0 için motor kapasitesi

# Motor DB filtreleme:
for m in MOTOR_DB:
    if |m.kV - kV_target| / kV_target > 25%: skip
    if m.P_max < P_req: skip
    if T_rise + T_ambient > m.T_max: skip

best = min(candidates, key=score)             # kV farkı + P_max fazlalığı
```

### Adım 2: Akım Hesabı

```python
I_hover = P_hover / (n_rotors × V_bat × eta_motor)   # hover akımı
I_peak  = P_motor_max / V_bat_nom                      # tam gaz (< 30s)
# Throttle @ hover: I_hover / I_max ≈ 0.50  (T/W=2 sağlar)
```

### Adım 3: Motor Verimi & Sıcaklık

```python
P_heat   = P_motor_req × (1 - eta_motor)
R_therm  = 10.0 / (P_max_kW)              # C/W ampirik tahmin
T_rise   = P_heat × R_therm
T_motor  = T_ambient + T_rise
# KK-12: T_motor ≤ T_max_motor (katalogdan)
```

### Adım 4: ESC Seçimi

```python
I_ESC_min   = I_peak × 1.25              # %25 marj
I_ESC_rated = standart değerlere yuvarla  # 20,30,40,60,80,100,120,150,200A
# V_ESC_max ≥ V_bat × 1.10
```

### Adım 5: İtki Zinciri Doğrulama

```
Pervane (BEMT) → Motor (eta_motor) → ESC (eta_ESC) → Batarya
    T_per_rot      P_shaft              P_ESC_out       P_bat_W
```

```python
T_total  = n_rotors × T_per_rotor
T_W      = T_total / (MTOW × g)         # KK-1: ≥ 2.0
T_W_OEI  = (n-1)×T_per / (MTOW×g)      # KK-2: ≥ 1.0
eta_sys  = eta_motor × eta_ESC × eta_kablo   # ≈ 0.85–0.87
P_bat    = P_hover / eta_sys
I_bat    = P_bat / V_bat_nom
```

### Adım 6: Toplam Sistem Verimi

```python
eta_sys = eta_motor × eta_ESC × eta_kablo
       ≈ 0.88 × 0.96 × 0.99 ≈ 0.836-0.87
P_bat_W   = P_hover_W / eta_sys
I_bat_tot = P_bat_W / V_bat_nom          # → WBS 4.1 batarya C-rate
```

---

## 📊 Motor Katalog Referansı (Seçkiler)

| Model | kV | P_max (W) | I_max (A) | m (g) | T_max | MTOW Hedef |
|-------|----|-----------|-----------|-------|-------|------------|
| T-Motor F60 PRO III | 1750 | 250 | 45 | 52 | 90°C | 0.5–2 kg |
| T-Motor U5 II | 400 | 500 | 22 | 175 | 90°C | 3–10 kg |
| T-Motor U8 II Lite | 100 | 1000 | 22 | 280 | 90°C | 10–30 kg |
| T-Motor MN601 | 170 | 1500 | 30 | 345 | 90°C | 15–50 kg |
| T-Motor MN701 | 100 | 2500 | 50 | 480 | 90°C | 30–100 kg |
| T-Motor MN1005 | 90 | 5000 | 80 | 1050 | 90°C | 60–200 kg |
| KDE7215XF-160 | 160 | 2200 | 55 | 390 | 85°C | 25–80 kg |

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| **KK-1** | T/W @ hover | ≥ 2.0 | Motor gücünü artır |
| **KK-2** | T/W @ OEI | ≥ 1.0 | n_rotors artır (WBS 2.1) |
| **KK-12** | T_motor | ≤ T_max | Soğutma ekle; motor büyüt |
| — | I_peak | ≤ I_ESC_rated | ESC'yi yükselt |
| — | RPM_err | ≤ %5 | Farklı kV seç |

---

## İtki Zinciri Güç Akışı

| Bileşim | Verim | Kayıp | Sıcaklık Artışı |
|---------|-------|-------|-----------------|
| Batarya (LiPo/Li-Ion) | 0.98 | %2 | ~5°C |
| ESC (FET anahtarlama) | 0.96 | %4 | 10–20°C |
| Motor (sargı+çekirdek) | 0.88–0.92 | %8–12 | 15–30°C |
| Pervane (aerodinamik) | FM=0.60–0.75 | %25–40 | ~0°C |
| **Toplam** | **~0.85** | **~%15** | — |

---

## motor_esc.json Şeması (Pydantic MotorESCResult)

```python
class MotorESCResult(BaseModel):
    motor_model:       str
    kV_recommend:      int
    kV_actual:         int
    RPM_actual:        float
    RPM_err_pct:       float
    P_motor_max_W:     float
    I_hover_A:         float
    I_peak_A:          float
    eta_motor:         float     # 0–1
    T_rise_C:          float
    T_motor_C:         float     # KK-12: ≤ T_max
    KK12_pass:         bool
    ESC_model:         str
    I_ESC_rated_A:     int
    eta_system:        float
    P_bat_W:           float     # → WBS 4.1
    I_bat_total_A:     float     # → WBS 4.1 C-rate
    T_W_ratio:         float     # KK-1: ≥ 2.0
    T_W_OEI:           float     # KK-2: ≥ 1.0
    KK1_pass:          bool
    KK2_pass:          bool
    thrust_chain_ok:   bool
    validation_passed: bool = True
```

---

*WBS 3.9 Motor & ESC Seçimi Detay Rehberi v4.0 — Nisan 2026*  
*6 Adım | kV Doğrulama | T-Motor/KDE DB | İtki Zinciri | KK-1/2/12 | Pydantic MotorESCResult*
