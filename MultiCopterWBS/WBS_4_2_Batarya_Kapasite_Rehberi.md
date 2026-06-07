# ⚡ WBS 4.2 v1.0 — BATARYA KAPASİTE & S/P KONFİGÜRASYONU

> **Peukert Kaybı | KK-3 Dayanım | Seri-Paralel Optimizasyonu | Pydantic BatterySizeResult**

> **Versiyon Notu (Mayıs 2026):** WBS 4.1 v2 ile uyumlu; SSS/ASS kimyaları için DoD ve Peukert parametreleri güncellendi.

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 4.2 v1.0 |
| **Bağımlılık** | WBS 4.1 battery_chem.json → WBS 3.9 thrust_chain.json |
| **Çıktı** | battery.json + Pydantic BatterySizeResult |
| **KK** | KK-3: t_hover ≥ req × 1.20 |

---

## 🔟 6 Adımlı Algoritma

### Adım 1: Girdi Okuma

```python
P_hover      = thrust_chain['P_total_hover_W']
I_total      = thrust_chain['I_total_A']
Wh_kg        = chem['Wh_kg_actual']
DoD          = chem.get('DoD', 0.80)         # kimyaya göre: LiPo 0.80 / SSS 0.85 / ASS 0.90
n_Peukert    = chem.get('n_Peukert', 1.05)
endurance_min = requirements['endurance_min']
```

### Adım 2: Enerji Gereksinimi

```python
E_bat_min    = P_hover * (endurance_min / 60) / 0.85   # η_batt = 0.85
E_bat_design = E_bat_min / (DoD * 0.80)                # %20 rezerv
```

### Adım 3: S×P Konfigürasyon

```python
n_series   = round(V_nom_req / V_cell_nom)
V_pack     = n_series * V_cell_nom
C_mAh_req  = E_bat_design / V_pack * 1000
P_cap      = ceil(C_mAh_req / C_cell_mAh)

# C-rate kısıtı paralel sayıyı artırabilir
P_crate    = ceil((I_total / P_cap) / C_cell_mAh * 1000 / C_rate_max)
n_parallel = max(P_cap, P_crate)
```

### Adım 4: Peukert Düzeltmesi

```python
# Peukert modeli: C_eff = C_nom × (I_nom / I_actual)^(n-1)
I_per_cell    = I_total / n_parallel
I_nom_1C      = C_mAh_actual / 1000
t_nom_min     = (C_mAh_actual/1000) / I_per_cell * 60 * DoD * 0.80
t_Peukert_min = t_nom_min * (I_nom_1C / I_per_cell) ** (n_Peukert - 1)
```

### Adım 5: Kütle & C-Rate Kontrol

```python
m_bat_kg     = E_actual_Wh / Wh_kg
C_rate_actual = I_total / (n_parallel * C_mAh_actual / 1000)
C_rate_ok     = C_rate_actual <= C_rate_max
mass_ok       = m_bat_kg <= max_bat_mass_kg
```

### Adım 6: KK-3 Kontrolü

```python
KK3_pass = t_Peukert_min >= endurance_min * 1.20
# Başarısız → n_parallel artır veya Wh/kg daha yüksek kimyaya geç
```

---

## 📊 S×P Referans Tablosu (2026)

| Konfig | Kimya | V_nom | C_bat_Wh | C-rate | Kütle | Dayanım +% |
|--------|-------|-------|----------|--------|-------|-----------|
| 6S1P | LiPo (ref) | 22.2V | 300 Wh | ~12C | 1.50 kg | 0% |
| 6S1P | SSS 290 Wh/kg | 22.2V | 435 Wh | ~8C | 1.50 kg | **+45%** |
| 6S1P | SSS 375 Wh/kg | 22.2V | 563 Wh | ~6C | 1.50 kg | **+88%** |
| 6S1P | ASS 350 Wh/kg | 22.2V | 525 Wh | ~3C (!) | 1.50 kg | +75% |
| 8S1P | SSS 375 Wh/kg | 29.6V | 750 Wh | ~5C | 2.00 kg | +88% |

---

## 📐 DoD & Rezerv Tablosu

| Kimya | DoD | Rezerv | Efektif Kullanım | Peukert n |
|-------|-----|--------|-----------------|-----------|
| LiPo | 80% | 20% | 64% | 1.05 |
| SSS (270-320) | 85% | 20% | 68% | 1.06 |
| SSS (350-400) | 88% | 20% | 70% | 1.06 |
| ASS Pilot | 90% | 20% | 72% | 1.04 |

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| **KK-3** | t_hover_Peukert | ≥ req × 1.20 | n_parallel ++ veya Wh/kg yükselt |
| — | C_rate_discharge | ≤ C_rate_max | n_parallel artır |
| — | m_bat_kg | ≤ max_bat_mass_kg | Wh/kg artır; SSS/ASS değerlendir |
| — | Peukert dahil | Zorunlu | n_Peukert chem'den alınmalı |

---

## BatterySizeResult Şeması

```python
class BatterySizeResult(BaseModel):
    S:                int
    P:                int
    V_nom:            float
    C_mAh:            int
    E_Wh:             float
    weight_kg:        float
    discharge_C:      float
    C_rate_ok:        bool
    mass_ok:          bool
    t_hover_min:      float            # KK-3 — Peukert dahil
    KK3_pass:         bool
    reserve_pct:      float = 20.0
    Peukert_n:        float
    validation_passed: bool = True
```

---

*WBS 4.2 v1.0 — Mayıs 2026 | Peukert Modeli | KK-3 Otomatik | Pydantic BatterySizeResult*
