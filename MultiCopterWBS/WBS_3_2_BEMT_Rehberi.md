# 🍃 WBS 3.2 — BLADE ELEMENT MOMENTUM TEORİSİ (BEMT)

> **Blade Elemanı Ayrıştırma | C_L C_D Dağılımı | Gerçek FM | Q_drag | KK-5 FM ≥ 0.60**  
> Leishman §3 | Glauert BEMT | NDARC §4 | UIUC Airfoil DB | Pydantic BEMTResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 3.2 |
| **Faz** | AŞAMA 3 — Aerodinamik & Tahrik Analizi |
| **Görev** | Blade Element Momentum Analizi |
| **Girdi** | `hover.json` (WBS 3.1) + `geometry.json` (WBS 2.2) + `blade_params.json` |
| **LLM Script** | `bemt.py` |
| **Çıktı** | `bemt.json`: FM_actual, Q_drag_Nm, RPM_hover, CT, CP, V_tip_ms |
| **Kabul Kriteri** | KK-5: FM_actual ≥ 0.60 \| BEMT yakınsadı \| Q_drag → WBS 2.3 güncelleme \| Pydantic PASS |
| **Sonraki WBS** | WBS 2.2 (D iteratif) \| WBS 2.3 (Q_drag) \| WBS 3.3 İleri Uçuş \| WBS 3.9 Motor |
| **Standartlar** | Leishman §3 \| Glauert 1926 \| NDARC §4 \| UIUC Airfoil DB \| Johnson §3 |

---

## 🔟 7 Adımlı Algoritma

### Adım 1: Blade Parametreleri

```python
# Chord dağılımı (taper):
chord(r) = c_ref * (1 - (1-taper)*(r/R - 0.2)/0.8)
sigma    = n_b * c * R / (pi * R^2)   # solidity → tipik: 0.05-0.10

# Twist dağılımı (lineer):
theta(r) = twist_root + (twist_tip - twist_root) * r/R
```

### Adım 2: Radyal Eleman Bölümleme

```python
N_elem = 20                           # eleman sayısı
r_i    = (i + 0.5) / N * R           # eleman merkezi
dr     = R / N                        # eleman genişliği
```

### Adım 3: İnflow Hızı & Açısı (Glauert İterasyonu)

```python
for each element i:
    phi_i   = arctan(lambda_i / r_bar_i)
    alpha_i = theta_i - phi_i

    # Glauert inflow güncellemesi:
    lambda_new = sigma*CL/(8*F) * (sqrt(1 + 32*F*theta*r_bar/(sigma*CL)) - 1) / 4
    lambda_i   = 0.5*(lambda_new + lambda_old)   # underrelax
# Yakınsama: |lambda_new - lambda_old| < 1e-5
```

### Adım 4: CL & CD Katsayıları

```python
CL_i = CL_alpha * alpha_i       # CL_alpha ≈ 2π /rad; stall: CL ≤ 1.4
CD_i = CD_0 + k * CL_i^2        # CD_0 tipik: 0.010-0.015 (Clark-Y)

# Prandtl uç kayıp faktörü:
f    = n_b/2 * (1 - r/R) / (r/R * sin(phi))
F    = (2/π) * arccos(exp(-f))
```

### Adım 5: Element İtki & Tork

```python
dT/dr = F * n_b * 0.5*rho*(Ω*r)^2 * c * (CL*cos(φ) - CD*sin(φ))
dQ/dr = F * n_b * 0.5*rho*(Ω*r)^2 * c * r * (CD*cos(φ) + CL*sin(φ))
T = Σ(dT/dr * dr)   Q = Σ(dQ/dr * dr)
```

### Adım 6: FM, CT, CP

```python
CT = T / (rho * A * (Ω*R)^2)
CP = (Q*Ω) / (rho * A * (Ω*R)^3)
FM = CT^(3/2) / (√2 * CP)        # = P_ideal / P_actual
# KK-5: FM ≥ 0.60
```

### Adım 7: Geri Bildirim Döngüleri

```
bemt.json: FM_actual, Q_drag_Nm
    ├── → WBS 2.2: DL_actual ile D_rotor güncelle (ΔDL ≤ 5%)
    ├── → WBS 2.3: Q_drag_Nm ile yaw_balance revize
    └── → WBS 3.1: FM_actual ile P_hover rafine
```

---

## 📊 FM Hassasiyet Özeti

| Değişken | Etki | FM Değişimi |
|----------|------|-------------|
| n_blade: 2→3 | FM+ | +3% |
| n_blade: 2→4 | FM+ | +5% |
| Twist: 0→−10° | FM+ | +2% |
| Twist: 0→−15° | FM+ | +5% |
| Airfoil: Clark-Y→E387 | FM+ | +8% |
| Airfoil: Clark-Y→NACA 0012 | FM− | −5% |
| sigma: 0.07→0.04 | FM− | −7% |
| Prandtl F eklenmesi | FM− | −1% (gerçekçi) |

---

## 📐 Airfoil Seçim Rehberi

| Profil | CD_0 | FM Etkisi | Re Aralığı | Kullanım |
|--------|------|-----------|------------|----------|
| E387 | 0.007 | Çok iyi | 50k–500k | Küçük UAV |
| MH-114 | 0.008 | Çok iyi | 100k–1M | Modern UAV |
| Clark-Y | 0.011 | İyi | 100k–1M | Ticari UAV |
| NACA 4412 | 0.010 | İyi | 100k–2M | Genel |
| NACA 0012 | 0.012 | Orta | 50k–2M | Test |

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| **KK-5** | FM_actual | ≥ 0.60 | Airfoil/twist/chord iyileştir |
| — | bemt_converged | True | N_elem artır; underrelax azalt |
| — | V_tip | < 240 m/s | RPM azalt; D artır |
| — | alpha_i | < alpha_stall | Twist/chord ayarla |

---

## bemt.json Şeması (Pydantic BEMTResult)

```python
class BEMTResult(BaseModel):
    n_blades:          int
    D_rotor_m:         float
    RPM_hover:         float    # gt=0
    V_tip_ms:          float    # gt=0
    CT:                float    # gt=0
    CP:                float    # gt=0
    FM_actual:         float    # 0–0.95  (KK-5 ≥ 0.60)
    Q_drag_Nm:         float    # gt=0  → WBS 2.3
    T_calc_N:          float
    P_actual_W:        float
    DL_actual_Nm2:     float    # → WBS 2.2 iterasyon
    bemt_converged:    bool
    KK5_pass:          bool
    validation_passed: bool = True
```

---

*WBS 3.2 BEMT Detay Rehberi v4.0 — Nisan 2026*  
*7 Adım | Glauert İterasyonu | Prandtl Uç Kayıp | KK-5 FM ≥ 0.60 | Pydantic BEMTResult*
