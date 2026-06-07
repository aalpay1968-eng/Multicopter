# ✈️ WBS 3.3 — GROUND EFFECT ANALİZİ (Cheeseman-Bennett)

> **T_IGE/T_OGE Oranı | Kalkış Profili | OGE Geçiş Yüksekliği | Enerji Tasarrufu**  
> Cheeseman & Bennett 1955 | Leishman §2.13 | NDARC §4.2 | Pydantic GroundEffectResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 3.3 |
| **Faz** | AŞAMA 3 — İtki Sistemi & BEMT Analizi |
| **Görev** | Ground Effect (Zemin Etkisi) Analizi |
| **Girdi** | `bemt.json` (WBS 3.2) + `geometry.json` (WBS 2.2) + `landing_gear.json` (WBS 2.7) |
| **LLM Script** | `ground_effect.py` |
| **Çıktı** | `ground_effect.json`: T_IGE_N, T_IGE_ratio, z_OGE_m, P_IGE_W, energy_saving_pct, takeoff_profile[] |
| **Kabul Kriteri** | T_IGE_ratio ≥ 1.0 \| P_IGE ≤ P_OGE \| Pydantic PASS |
| **Sonraki WBS** | WBS 3.4 Coaxial BEMT \| WBS 5.5 IGE-OGE Geçiş \| WBS 9.3 Kalkış Prosedürü \| WBS 4.1 Batarya |
| **Standartlar** | Cheeseman & Bennett 1955 \| Leishman §2.13 \| NDARC §4.2 \| Johnson §2.6 |

---

## 🔑 Cheeseman-Bennett Formülü

$$\frac{T_{IGE}}{T_{OGE}} = \frac{1}{1 - \left(\frac{D}{4z}\right)^2}$$

- **D** = rotor çapı (m)
- **z** = rotor disk merkezinin yerden yüksekliği (m)
- Geçerlilik: z ≥ D/4 (zemin teması öncesi)
- z = D/4'te: T_IGE/T_OGE → pratik sınır ≈ 1.80
- z ≥ D'de: etki ≤ %7 (pratik OGE)

**Güç ilişkisi:**
$$P_{IGE} = \frac{P_{OGE}}{T_{IGE}/T_{OGE}} \quad \text{(daha az güç gerekir)}$$

---

## 📊 IGE-OGE Geçiş Tablosu

| z/D | T_IGE/T_OGE | Güç Tasarrufu | Etki Düzeyi | Pratik Durum |
|-----|-------------|---------------|-------------|--------------|
| 0.25 | ~1.80 | ~%44 | Maksimum | Zemin temas sınırı |
| 0.50 | 1.333 | %25 | Kuvvetli | Tipik IGE hover |
| 0.75 | 1.128 | %11 | Orta | Alçak hover |
| **1.00** | **1.067** | **%6** | **Zayıf** | **OGE geçiş sınırı** |
| 1.50 | 1.025 | %2 | İhmal edilir | Pratik OGE |
| 2.00 | 1.010 | %1 | Yok | Tam OGE |

---

## 🚀 Kalkış Güç Profili

| Adım | Faz | z/D | T_IGE_ratio | P/P_OGE |
|------|-----|-----|-------------|---------|
| 1 | Spooling Up (0–2s) | 0 | 1.0 | 0→1.0 |
| 2 | IGE Hover (2–7s) | ~0.3D | ~1.30 | ~0.77 |
| 3 | IGE Kalkış (7–10s) | 0.3D→D | 1.30→1.01 | 0.77→0.99 |
| 4 | OGE Geçiş (10–11s) | ~D | ~1.01 | ~0.99 |
| 5 | Normal Climb (11s+) | ≥D | 1.0 | 1.0 |

---

## 🔟 4 Adımlı Algoritma

### Adım 1: T_IGE ve P_IGE Hesabı

```python
z_disk_IGE  = leg_height + 0.10        # disk merkezi yerden yükseklik
T_IGE_ratio = 1 / (1 - (D/(4*z))^2)   # Cheeseman-Bennett
T_IGE       = T_OGE * T_IGE_ratio
P_IGE       = P_OGE / T_IGE_ratio      # güç tasarrufu

# Coaxial: üst/alt rotor ayrı z değerleriyle ortalama
```

### Adım 2: OGE Geçiş Yüksekliği

```python
# T_IGE/T_OGE ≤ 1.01 → pratik OGE
z_OGE = D / (4 * sqrt(1 - 1/1.01))    # ≈ D (bir rotor çapı)
```

### Adım 3: Kalkış Profili

```python
for z_i in z_values:   # IGE'den OGE'ye kademeli yükselme
    ratio_i = CB_ratio(D, z_i)
    P_i     = P_OGE / ratio_i
    profile.append({'z_m': z_i, 'T_ratio': ratio_i, 'P_W': P_i})
```

### Adım 4: Enerji Tasarrufu

```python
E_IGE  = P_IGE * t_IGE_hover / 3600   # Wh
E_OGE  = P_OGE * t_IGE_hover / 3600   # Wh (referans)
saving = (E_OGE - E_IGE)              # Wh tasarruf
# WBS 4.1'de batarya hesabına dahil edilir
```

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| — | T_IGE_ratio | ≥ 1.0 | Formül/giriş kontrolü |
| — | P_IGE_W | ≤ P_OGE_W | Fizik ihlali; z kontrolü |
| — | z_OGE_m | > 0 | Geometri kontrolü |
| — | Pydantic | PASS | Parametreleri düzelt |

---

## 🔗 WBS Bağlantıları

```
bemt.json (WBS 3.2)        ──┐
geometry.json (WBS 2.2)   ──┤── ground_effect.py ──► ground_effect.json
landing_gear.json (WBS 2.7)─┘           │
                                          ├── WBS 5.5 ige_transition.py
                                          ├── WBS 9.3 landing_procedure.py
                                          └── WBS 4.1 battery_size.py (E_saving_Wh)
```

---

*WBS 3.3 Ground Effect Analizi Detay Rehberi v4.0 — Nisan 2026*  
*4 Adım | Cheeseman-Bennett 1955 | IGE-OGE Geçiş | Kalkış Profili | Pydantic GroundEffectResult*
