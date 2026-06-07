# 🚁 WBS 2.1 — ROTOR SAYISI & DİZİLİM SEÇİMİ

> **14 konfigürasyon tipi | 5 Adım Karar Algoritması | CW/CCW Dönüş Yön Ataması**  
> Payload filtresi | OEI doğrulama | Yaw Torque dengesi | Pydantic ConfigResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 2.1 |
| **Faz** | AŞAMA 2 — Konfigürasyon & 3D Geometri |
| **Görev** | Rotor Sayısı & Dizilim Seçimi |
| **Girdi** | `tradeoff.json` (WBS 1.5) + `requirements.json` (WBS 1.2) + `regulation.json` (WBS 1.3) |
| **LLM Script** | `config_select.py` |
| **Çıktı** | `config.json`: n_rotors, layout, coaxial_flag, arm_fold_flag, redundancy, rotation_dirs[], motor_positions_m[], yaw_balanced_flag |
| **Kabul Kriteri** | Konfigürasyon gerekçeli; rotation_dirs[] CW/CCW atanmış; OEI ≥ min; Pydantic doğrulama geçilmiş |
| **Sonraki WBS** | WBS 2.2 Rotor Çapı & Wheelbase → WBS 2.3 Yaw Torque Dengesi → WBS 7.2 Motor Mixing |
| **Standartlar** | NDARC NASA/TM-2015-218751 \| Prouty Rotorcraft Aero \| EASA SC-VTOL §2530 \| Mahony 2012 |

---

## 🔟 5 Adımlı Algoritma

### Adım 1: Payload & OEI'dan n_min Belirleme

```python
def n_min_from_payload(p_kg):
    if p_kg <= 3:   return 4    # Quad
    if p_kg <= 15:  return 6    # Hex
    if p_kg <= 50:  return 8    # Octo
    if p_kg <= 150: return 12   # Dodeca
    return 16                   # Hexadeca+

def n_min_from_OEI(sail_level, bvlos):
    if bvlos or sail_level >= 3: return 6   # N+1 zorunlu
    if sail_level >= 5:          return 8   # N+2
    return 4                                # N (SAIL I-II)

n_rotors = max(n_trade, n_min_from_payload(payload_kg), n_min_from_OEI(sail_req, BVLOS))
# Geçerli değerlere yuvarla: {4, 6, 8, 12, 16, 18, 24, 32}
```

### Adım 2: Layout Seçimi

| n_rotors | Coaxial | Görev Tipi | Layout |
|----------|---------|-----------|--------|
| 4 | False | Genel | `X-4` |
| 4 | False | Fotoğraf | `+-4` |
| 6 | False | Kargo/Gözetleme | `X-6` |
| 6 | False | Fotoğraf/LiDAR | `H-6` |
| 6 | True | Dar alan | `Y6-coax` |
| 8 | False | Ağır kargo | `X-8` |
| 8 | True | Kompakt yüksek yük | `X4-coax` |
| 12 | False | Endüstriyel | `X-12` |
| 12 | True | GRIFF tipi | `Hex-coax` |
| 16 | False | Büyük lojistik | `X-16` |
| 18 | False | DEP eVTOL | `DEP-ring` |
| 32 | False | Ağır DEP | `DEP-matrix` |

> **Kural:** Fotoğraf/harita görevi → H-frame (gimbal altında boşluk). Kargo → X (maksimum simetri). Dar alan → Y6 veya X4-coax.

### Adım 3: Motor Konumları

```python
def compute_motor_positions(n, arm_r_m, coax):
    if coax:
        n_arms = n // 2
        for i in range(n_arms):
            phi = radians(i * 360 / n_arms)
            positions += [[arm_r * cos(phi), arm_r * sin(phi), +0.05],   # üst
                          [arm_r * cos(phi), arm_r * sin(phi), -0.05]]   # alt
    else:
        for i in range(n):
            phi = radians(i * 360 / n)
            positions += [[arm_r * cos(phi), arm_r * sin(phi), 0.0]]
    return positions
# → WBS 2.2'den güncel wheelbase alındıktan sonra yeniden hesaplanır
```

### Adım 4: Dönüş Yönü Ataması (CW/CCW)

**Temel Kural:** `Σ(Q_CW) = Σ(Q_CCW)` → `|Q_yaw_imbalance| ≤ 0.01 N·m`

| Konfigürasyon | Motor Sırası | Dönüş Yönleri |
|---------------|-------------|----------------|
| **Quad-X (n=4)** | M1, M2, M3, M4 | CW, CW, CCW, CCW *(köşegen çiftler)* |
| **Hex-X (n=6)** | M1…M6 | CW, CCW, CW, CCW, CW, CCW *(alternating)* |
| **Octo-X8 (n=8)** | M1…M8 | CW, CCW, CW, CCW, CW, CCW, CW, CCW |
| **Y6-Coax (6 motor, 3 kol)** | Kol1-üst/alt, Kol2-üst/alt, Kol3-üst/alt | CCW/CW, CCW/CW, CCW/CW |
| **Hex-Coax (12 motor, 6 kol)** | Her kol: üst/alt | CCW/CW × 6 kol |
| **X-12 flat (n=12)** | M1…M12 | CW, CCW, … alternating (6 CW + 6 CCW) |

```python
def assign_rotation_dirs(n, coax):
    if coax:
        n_arms = n // 2
        return ['CCW' if i % 2 == 0 else 'CW' for i in range(n)]  # üst=CCW, alt=CW
    else:
        return ['CW' if i % 2 == 1 else 'CCW' for i in range(1, n+1)]
```

> ⚠️ Yaw torque doğrulaması WBS 2.3 `yaw_balance.py` ile yapılır. WBS 2.1'de sadece sayısal denge (`n_CW == n_CCW`) kontrol edilir.

### Adım 5: OEI Doğrulama

```python
def check_OEI(n, coax, MTOW_kg, T_total_N):
    n_fail = 2 if coax else 1          # Coaxial: 1 kol = 2 motor kaybı
    T_remain = (n - n_fail) / n * T_total_N
    T_W_OEI  = T_remain / (MTOW_kg * 9.81)
    return T_W_OEI, T_W_OEI >= 1.0    # Kabul: ≥ 1.0

# OEI geçemezse → n_rotors artır ve tekrar hesapla
```

**OEI Hızlı Tablo (T/W=2.0 varsayımı):**

| n Rotor | Coaxial | Arıza Motor | T Kayıp% | T/W_OEI | Kabul? |
|---------|---------|-------------|----------|---------|--------|
| 4 | Hayır | 1 | 25.0% | 1.50 | ✗ Hayır *(pratik kontrol yok)* |
| 6 | Hayır | 1 | 16.7% | 1.67 | ✓ Evet |
| 6 | Evet (Y6) | 2 (1 kol) | 33.3% | 1.33 | ✓ Kısıtlı |
| 8 | Hayır | 1 | 12.5% | 1.75 | ✓ Evet |
| 8 | Evet | 2 (1 kol) | 25.0% | 1.50 | ✓ Evet |
| 12 | Hayır | 1 | 8.3% | 1.83 | ✓ Evet |
| 16 | Hayır | 1 | 6.3% | 1.87 | ✓ Evet |

---

## 🚁 14 Konfigürasyon Özeti

| ID | Konfigürasyon | N | Kol | Layout | OEI | SAIL Max | Payload |
|----|---------------|---|-----|--------|-----|---------|---------|
| **C01** | Quadcopter-X | 4 | 4 | X-4 | N | SAIL-II | 0–3 kg |
| **C02** | Quadcopter-+ | 4 | 4 | +-4 | N | SAIL-II | 0–3 kg |
| **C03** | Hexacopter-X | 6 | 6 | X-6 | N+1 | SAIL-IV | 2–8 kg |
| **C04** | Hexacopter-H | 6 | 6 | H-6 | N+1 | SAIL-IV | 2–8 kg |
| **C05** | Y6 Coaxial Tricopter | 6 | 3 | Y6-coax | Koşullu N+1 | SAIL-III | 2–8 kg |
| **C06** | Octocopter-X8 flat | 8 | 8 | X-8 | N+2 | SAIL-V | 5–15 kg |
| **C07** | Octocopter X4 Coaxial | 8 | 4 | X4-coax | N+2 | SAIL-V | 5–15 kg |
| **C08** | Dodecacopter-X12 | 12 | 12 | X-12 | N+3 | SAIL-V | 15–50 kg |
| **C09** | Coaxial Hexacopter-12 | 12 | 6 | Hex-coax | N+2 | SAIL-V | 12–45 kg |
| **C10** | Hexadecacopter-X16 | 16 | 16 | X-16 | N+4 | SAIL-VI | 25–80 kg |
| **C11** | DEP-18 Dağıtık | 18 | 18 | DEP-ring | N+6+ | Certified | 40–120 kg |
| **C12** | eVTOL Tilt-Prop Hibrit | 8 | 8 | Tilt-prop | N+2 | Certified | 100–400 kg |
| **C13** | Büyük X4-Coaxial | 8 | 4 | X4-coax-L | N+2 | Certified | 150–600 kg |
| **C14** | DEP-32 Modüler | 32 | 32 | DEP-matrix | N+8+ | Certified | 600–2000 kg |

---

## 🔑 Hızlı Karar Ağacı

```
IF payload > 50 kg           → C08 (Dodeca-X12) veya C09 (Hex-coax)
IF payload > 150 kg          → C10 (X-16) veya C11 (DEP-18)
IF payload > 400 kg          → C12/C13/C14 (Hibrit/Coax/DEP)
IF payload > 10 kg
    IF kompakt wheelbase      → C07 (X4-coax)
    ELSE                      → C06 (Octo-X8)
IF BVLOS veya SAIL ≥ III
    IF payload < 8 kg         → C03 (Hex-X) veya C04 (Hex-H)
    IF fotoğraf/lidar görevi  → C04 (Hex-H)
IF dar alan (indoor)         → C05 (Y6-coax) veya C07 (X4-coax)
IF payload < 3 kg, hobbyist  → C01 (Quad-X)
DEFAULT                      → C03 (Hex-X)  ← en yaygın seçim
→ config_select.py ile doğrula → config.json
```

---

## 📐 config.json Şeması (Pydantic ConfigResult)

```python
class ConfigResult(BaseModel):
    n_rotors:          int               # 4, 6, 8, 12, 16, 18, 24, 32
    layout:            str               # 'X-4', 'X-6', 'H-6', 'Y6-coax', 'X-8'...
    coaxial_flag:      bool              # True → çift katlı rotor
    arm_fold_flag:     bool              # True → katlanabilir kol (+%5 kütle)
    redundancy:        str               # 'N', 'N+1', 'N+2', 'N+3', ...
    rotation_dirs:     List['CW'|'CCW'] # Uzunluk = n_rotors
    motor_positions_m: List[List[float]] # [n_rotors × 3] [x, y, z] m
    T_W_OEI:           float             # OEI T/W oranı ≥ 1.0
    OEI_OK:            bool              # True → kabul
    yaw_balanced_flag: bool              # True → n_CW == n_CCW
    drive_type:        str               # 'electric', 'hybrid', 'turbine'
    validation_passed: bool = True
```

**Validator kuralları:**
- `rotation_dirs`: `count('CW') == count('CCW')` → yaw dengesi
- `T_W_OEI`: `≥ 1.0` → OEI kontrollü iniş mümkün

---

## 🔗 WBS Bağlantıları

```
WBS 1.2 requirements.json ──┐
WBS 1.3 regulation.json ────┤
WBS 1.5 tradeoff.json ──────┴── WBS 2.1 config_select.py ──► config.json
                                        │
                    ┌───────────────────┼───────────────────────┐
                    ▼                   ▼                        ▼
           WBS 2.2 geometry     WBS 2.3 yaw_balance     WBS 7.2 mixing
         (wheelbase, D_rotor)  (Q_imbalance ≤ 0.01 N·m) (B_matrix, rank=4)
```

---

## ⚠️ Kritik Kontrol Noktaları

| Kontrol | Kriter | Referans |
|---------|--------|----------|
| OEI T/W oranı | T/W_OEI ≥ 1.0 (kabul) | EASA SC-VTOL §2530 |
| Yaw denge (sayısal) | n_CW == n_CCW | Mahony 2012 |
| Yaw torque (fiziksel) | \|Q_imbalance\| ≤ 0.01 N·m | WBS 2.3 (KK-13) |
| Motor mixing matrisi | rank(B) = 4 ; cond(B) < 50 | WBS 7.2 |
| Layout uyumu | T/W ≥ 2.0 @ hover | WBS 3.9 (KK-1) |
| SAIL uyumu | Seçilen n → SAIL gereksinimi | WBS 1.3 |

---

*WBS 2.1 Rotor Sayısı & Dizilim Seçimi Detay Rehberi v4.0 — Nisan 2026*  
*14 Konfigürasyon | 5 Adım Algoritma | Pydantic ConfigResult | CW/CCW Atama Tabloları*
