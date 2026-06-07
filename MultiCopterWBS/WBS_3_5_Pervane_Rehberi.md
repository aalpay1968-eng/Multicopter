# 🔩 WBS 3.5 — PERVANE SEÇİMİ & MOTOR UYUMU

> **CT/CP Eşdeğerliği | RPM-T-Q Eşleştirme | APC/T-Motor/Mejzlik DB | kV Hesabı**  
> APC Prop DB | UIUC DB | Leishman §3 | Pydantic PropMatchResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 3.5 |
| **Faz** | AŞAMA 3 — İtki Sistemi & BEMT Analizi |
| **Görev** | Pervane Seçimi & Motor kV Uyumu |
| **Girdi** | `bemt.json` (WBS 3.2) + `coax.json` (WBS 3.4) + `requirements.json` |
| **LLM Script** | `prop_match.py` |
| **Çıktı** | `prop_match.json`: prop_model, CT_match, CP_match, FM_match, kV_recommend, V_bat_S |
| **Kabul Kriteri** | FM_match ≥ 0.60 (KK-5) \| V_tip < 240 m/s \| T_err ≤ %5 \| Pydantic PASS |
| **Sonraki WBS** | WBS 3.6 Gürültü \| WBS 3.9 Motor Seçimi \| WBS 12.1 BOM |
| **Standartlar** | APC Propeller DB \| UIUC Propeller DB \| T-Motor DB \| EASA CS-23 Amdt 5 |

---

## 🔟 5 Adımlı Algoritma

### Adım 1: Hedef CT ve CP Hesabı

```python
CT_target = T / (rho × A × (Ω×R)²)    # bemt.json'dan
CP_target = P / (rho × A × (Ω×R)³)    # bemt.json'dan
D_in      = D_rotor_m × 39.37          # m → inch
```

### Adım 2: Veritabanı Eşleşme

```python
for prop in PROP_DB:
    if |prop.D_in - D_in| > 1.5:  continue  # boyut filtresi
    score = 0.4×|CT_err| + 0.3×|CP_err| + 0.3×|FM_err|
    
best = min(candidates, key=lambda x: x['score'])
```

### Adım 3: Boyutsal Doğrulama

```python
V_tip     = Ω × R                      # < 240 m/s zorunlu
T_match   = rho × A × (Ω×R)² × CT_db  # hedef itkiyle karşılaştır
T_err_pct = |T_match - T_target| / T_target × 100   # ≤ %5
FM_match  = CT_db^(3/2) / (√2 × CP_db)             # ≥ 0.60 (KK-5)
```

### Adım 4: Motor kV Hesabı

```python
kV_recommend = RPM_hover / V_bat_nominal
V_bat_nominal = n_cells × V_cell_nominal   # LiPo: 3.7V/hücre
# Düşük kV → büyük pervane, ağır platform
# Yüksek kV → küçük pervane, hafif platform
```

**kV-Voltaj Uyum Tablosu:**

| Senaryo | D_rotor | RPM_hover | Batarya | kV öneri | Motor Örnek |
|---------|---------|-----------|---------|----------|-------------|
| Mini quad | 0.24 m | 6000 | 4S (14.8V) | 405 | T-Motor F60 PRO |
| Hex kargo | 0.38 m | 4500 | 6S (22.2V) | 203 | T-Motor U5 KV400 |
| Octo ağır | 0.55 m | 2800 | 8S (29.6V) | 95 | T-Motor MN601 |
| X12 endüstri | 0.65 m | 2200 | 10S (37.0V) | 59 | T-Motor MN801 |
| X16 büyük | 0.90 m | 1600 | 12S (44.4V) | 36 | T-Motor MN1005 |

### Adım 5: Final Seçim & Güvenlik Kontrolleri

```python
safety_pass = V_tip_ok and T_err_ok and FM_ok
# → prop_match.json yaz
# → WBS 3.6 gürültü (V_tip ile)
# → WBS 3.9 motor seçimi (kV ile)
# → WBS 12.1 BOM'a ekle
```

---

## 📊 Ticari Pervane Referans Özeti

| Model | D_in | Pitch | Kanat | CT | FM | MTOW Hedef |
|-------|------|-------|-------|----|----|------------|
| APC 10x4.7 SF | 10" | 4.7" | 2 | 0.108 | 0.70 | 1–3 kg |
| APC 15x5.5 MR | 15" | 5.5" | 2 | 0.110 | 0.70 | 5–12 kg |
| APC 18x6.1 E | 18" | 6.1" | 2 | 0.108 | 0.72 | 10–25 kg |
| T-Motor 22x7.2 CF | 22" | 7.2" | 2 | 0.112 | 0.72 | 20–50 kg |
| Mejzlik 27x9 E | 27" | 9.0" | 2 | 0.110 | 0.72 | 40–100 kg |
| T-Motor P18x6.1 3B | 18" | 6.1" | **3** | 0.125 | 0.68 | 15–40 kg |

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| **KK-5** | FM_match | ≥ 0.60 | Farklı pervane; BEMT optimizasyonu |
| — | V_tip | < 240 m/s | RPM azalt; D azalt |
| — | T_match_err | ≤ %5 | pitch veya RPM ayarla |
| — | safety_pass | True | Tüm kontroller PASS |

---

## prop_match.json Şeması (Pydantic PropMatchResult)

```python
class PropMatchResult(BaseModel):
    D_in_target:       float
    CT_target:         float
    CP_target:         float
    FM_target:         float
    selected_model:    str
    diameter_in:       float
    pitch_in:          float
    n_blades:          int
    CT_match:          float    # gt=0
    CP_match:          float    # gt=0
    FM_match:          float    # ≥ 0.60  (KK-5)
    T_match_N:         float
    T_match_err_pct:   float    # ≤ 5%
    V_tip_ms:          float    # < 240 m/s
    match_score:       float
    kV_recommend:      int
    V_bat_S:           str      # örn: '6S'
    n_cells:           int
    candidates_count:  int
    V_tip_ok:          bool
    T_err_ok:          bool
    FM_pass:           bool
    safety_pass:       bool
    validation_passed: bool = True
```

---

*WBS 3.5 Pervane Seçimi & Motor Uyumu Detay Rehberi v4.0 — Nisan 2026*  
*5 Adım | CT/CP Eşleşme | APC/T-Motor/Mejzlik DB | kV Hesabı | Pydantic PropMatchResult*
