# 🌀🌀 WBS 3.4 — COAXIAL ROTOR ANALİZİ

> **Üst-Alt Rotor Etkileşimi | k_int Faktörü | FM_coax | T/Q Dengesi**  
> Leishman §8 | Harrington 1951 | NDARC §4 | Pydantic CoaxResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 3.4 |
| **Faz** | AŞAMA 3 — İtki Sistemi & BEMT Analizi |
| **Görev** | Coaxial Rotor Etkileşim Analizi |
| **Atlama Koşulu** | `coaxial_flag = False` → **bu WBS atlanır**, `coax.json` boş üretilir |
| **Girdi** | `config.json` (WBS 2.1) + `bemt.json` (WBS 3.2) + `geometry.json` (WBS 2.2) |
| **LLM Script** | `coax_bemt.py` |
| **Çıktı** | `coax.json`: k_int, FM_coax, T_upper_N, T_lower_N, Q_net_Nm, axial_sep_opt_m |
| **Kabul Kriteri** | FM_coax ≥ 0.60 (KK-5) \| \|Q_net\| ≤ 0.01 N·m (KK-13) \| k_int ≤ 1.30 \| Pydantic PASS |
| **Sonraki WBS** | WBS 3.5 Pervane Seçimi \| WBS 2.3 Q_drag güncelle \| WBS 3.9 İtki Zinciri |
| **Standartlar** | Leishman §8 \| Harrington 1951 NACA TN-2229 \| NDARC §4 \| Coleman et al. 1945 |

---

## 🔑 Temel Kavramlar

**k_int (etkileşim faktörü):** Alt rotor, üst rotordan gelen uyarılmış akımla çalışır → inflow artar → aynı itki için daha fazla güç gerekir.

$$v_{i,lower} = v_{i,upper} \times \sqrt{k_{int}}$$

$$P_{lower} = P_{upper} \times k_{int}$$

**FM_coax:** Coaxial çiftin gerçek figure of merit'i, her zaman tek rotordan düşük.

$$FM_{coax} \approx FM_{single} \times \frac{\sqrt{2}}{1 + k_{int}^{3/2}}$$

---

## 🔟 5 Adımlı Algoritma

### Adım 1: k_int Hesabı

```python
def calc_k_int(D, sep):
    z_ratio = sep / D
    return 1.0 + 0.4 * (z_ratio) ** (-0.5)   # Leishman §8 yaklaşımı

# Önerilen: sep = 0.12–0.15 × D_rotor
# k_int = 1.0 (bağımsız) → 1.41 (tam etkileşim, teori maksimumu)
```

**Eksenel Ayrım Referans Tablosu:**

| z_sep/D | k_int | FM_coax (FM_s=0.65) | Güç Cezası | Durum |
|---------|-------|---------------------|------------|-------|
| 0.08 | 1.35 | 0.570 | %14 | Kötü — artır |
| 0.12 | 1.23 | 0.594 | %9 | Kabul |
| **0.15 (opt)** | **1.18** | **0.612** | **%6** | **Optimal** |
| 0.20 | 1.11 | 0.636 | %3 | Çok iyi |
| ≥0.30 | 1.0 | 0.650 | 0% | Tam bağımsız |

### Adım 2: Üst-Alt İtki Dağılımı

```python
T_upper = T_single                          # üst rotor: bağımsız (BEMT'den)
T_lower = T_upper / sqrt(k_int)             # alt rotor: daha az (~%88 k_int=1.20'de)
T_coax_pair = T_upper + T_lower
T_total     = n_arms * T_coax_pair
```

### Adım 3: FM_coax

```python
P_upper = Q_single * Omega
P_lower = P_upper * k_int                   # alt rotor daha fazla güç
P_total = n_arms * (P_upper + P_lower)

v_i     = sqrt(T_total / (2 * rho * n_arms * A_disk))
P_ideal = T_total * v_i
FM_coax = P_ideal / P_total                 # KK-5: ≥ 0.60
```

### Adım 4: Yaw Tork Dengesi

```python
Q_upper = Q_single          # CW → pozitif
Q_lower = Q_single * k_int  # CCW → negatif (büyüklük farklı)
Q_net   = Q_upper - Q_lower  # ≠ 0 (k_int nedeniyle)

# RPM trim ile düzeltme:
dQ_dRPM       = 2 * Q_single / RPM_hover
RPM_trim      = Q_net / (n_arms * dQ_dRPM)   # ±%1-3 RPM
# KK-13: |Q_net_trimmed| ≤ 0.01 N·m
```

### Adım 5: Optimal Sep Optimizasyonu

```python
best_FM = 0; best_sep = axial_sep
for sep_i in linspace(0.08*D, 0.25*D, 10):
    ki    = calc_k_int(D, sep_i)
    FM_i  = compute_FM_coax(ki)
    if FM_i > best_FM: best_FM, best_sep = FM_i, sep_i
# axial_sep_opt ≈ 0.12–0.15 × D
```

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| **KK-5 coax** | FM_coax | ≥ 0.60 | axial_sep artır; blade opt. |
| **KK-13 coax** | \|Q_net_trimmed\| | ≤ 0.01 N·m | RPM trim uygula; blade pitch fark |
| — | k_int | ≤ 1.30 | axial_sep artır (≥0.12D) |
| — | axial_sep | ≥ 0.08×D | Motor konumu WBS 2.2'de revize |

---

## coax.json Şeması (Pydantic CoaxResult)

```python
class CoaxResult(BaseModel):
    coaxial_flag:       bool
    n_arms:             int
    axial_sep_m:        float    # gt=0
    k_int:              float    # 1.0–1.41
    T_upper_N:          float
    T_lower_N:          float
    T_total_N:          float
    P_total_W:          float
    FM_coax:            float    # ≥ 0.60  (KK-5)
    Q_net_Nm:           float
    Q_net_trimmed_Nm:   float    # |val| ≤ 0.01  (KK-13)
    RPM_trim_delta:     float
    axial_sep_opt_m:    float
    FM_coax_pass:       bool
    KK13_coax_pass:     bool
    skipped:            bool     # coaxial_flag=False ise True
    validation_passed:  bool = True
```

---

*WBS 3.4 Coaxial Rotor Analizi Detay Rehberi v4.0 — Nisan 2026*  
*5 Adım | k_int Leishman §8 | FM_coax | KK-5 ≥ 0.60 | KK-13 ≤ 0.01 N·m | Pydantic CoaxResult*
