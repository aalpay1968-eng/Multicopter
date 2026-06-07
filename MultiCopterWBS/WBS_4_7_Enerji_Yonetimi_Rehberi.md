# ⏱️ WBS 4.7 v1.0 — ENERJİ YÖNETİMİ & UÇUŞ SÜRESİ TAHMİNİ

> **P(v) = P_hover + P_parasitik | Peukert | %20 Rezerv | Menzil Analizi | NDARC §4**

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 4.7 v1.0 |
| **Bağımlılık** | WBS 4.2 battery + WBS 3.9 thrust_chain + WBS 5.3 fwd_flight |
| **Çıktı** | energy_budget.json |
| **Standart** | NDARC §4 | Peukert 1897 | FAA AC 20-184 |

---

## 📈 Güç Profili Modeli

```
P(v) = P_hover × √(1 + (v/v_i)²/4 + (v/v_i)²/2)
     + ½ρA_frontal × v³                          (parasitik sürükleme)

v_i = √(T/(2ρA))  ← hover induced velocity
```

| Uçuş Hali | P_toplam / P_hover | t_mevcut | Not |
|-----------|-------------------|---------|-----|
| Hover | 1.00× | t_max | Maksimum süre |
| Verimli cruise | ~0.85× | t×1.18 | **Max menzil** |
| Normal cruise | ~0.90× | t×1.11 | Nominal görev |
| Max hız | ~1.50× | t×0.67 | Kısa; termal uyarı |

---

## 🔟 6 Adımlı Algoritma

```python
# ADIM 2: Kullanılabilir Enerji
E_usable = C_bat_Wh * DoD * 0.80    # %20 rezerv korunur
E_reserve = C_bat_Wh * DoD * 0.20   # korunan rezerv

# ADIM 3: Hover Süresi (Peukert dahil)
t_hover_nom = E_usable / P_hover * 60
t_hover = t_hover_nom * (I_nom_1C / I_per_cell) ** (n_Peukert - 1)

# ADIM 4: Cruise & Menzil
t_cruise = E_usable / P_cruise * 60
range_km = V_cruise_ms * t_cruise * 60 / 1000

# ADIM 5: Karma Görev
P_avg    = f_hover * P_hover + (1 - f_hover) * P_cruise
t_mixed  = E_usable / P_avg * 60
```

---

## 📊 Enerji Bütçe Özeti (Kimya Karşılaştırması)

| Kimya | Wh/kg | t_hover (ref = 20dk) | Menzil Artışı | Peukert Düzeltme |
|-------|-------|---------------------|-------------|-----------------|
| LiPo | 200 | 20 dk (ref) | 0% | −3% |
| SSS 290 | 290 | 29 dk | +45% | −4% |
| SSS 375 | 375 | 37.6 dk | +88% | −4% |
| ASS Pilot | 350 | 35 dk | +75% | −2% |

---

## ✅ Kabul Kriterleri

| Kriter | Limit |
|--------|-------|
| t_hover (Peukert dahil) | ≥ endurance_min |
| Rezerv | = 20% sabit |
| Menzil tutarlılığı | range_km = V_cruise × t_cruise |
| P_avg hesaplanmış | f_hover tanımlı |

---

## EnergyBudgetResult Şeması

```python
class EnergyBudgetResult(BaseModel):
    C_bat_Wh:       float
    E_usable_Wh:    float
    E_reserve_Wh:   float
    P_hover_W:      float
    P_cruise_W:     float
    P_avg_W:        float
    t_hover_min:    float
    t_cruise_min:   float
    t_mixed_min:    float
    range_km:       float
    reserve_pct:    float    # sabit 20.0
    Peukert_n:      float
    endurance_ok:   bool
    validation_passed: bool = True
```

---

*WBS 4.7 v1.0 — Mayıs 2026 | P(v) Güç Modeli | Peukert | %20 Rezerv | NDARC §4*
