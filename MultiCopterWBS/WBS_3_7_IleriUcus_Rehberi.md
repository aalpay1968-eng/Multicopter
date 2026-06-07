# ✈️ WBS 3.7 — İLERİ UÇUŞ ANALİZİ (Edgewise Flight)

> **Glauert Muavemeti | P_induced + P_profile + P_parasite | V_max | Menzil & Dayanım**  
> Leishman §2 | Glauert 1926 | Prouty §2 | Pydantic ForwardFlightResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 3.7 |
| **Faz** | AŞAMA 3 — İtki Sistemi & BEMT Analizi |
| **Görev** | İleri Uçuş Güç Analizi & Menzil |
| **Girdi** | `hover.json` (WBS 3.1) + `bemt.json` (WBS 3.2) + `geometry.json` (WBS 2.2) + `requirements.json` |
| **LLM Script** | `forward_flight.py` |
| **Çıktı** | `forward_flight.json`: P_cruise_W, V_max_ms, V_opt_ms, range_km, endurance_min, L/D, energy_profile[] |
| **Kabul Kriteri** | V_cruise ≤ V_max \| range ≥ range_req \| L/D ≥ 2.0 \| Pydantic PASS |
| **Sonraki WBS** | WBS 3.8 Enerji Bütçesi \| WBS 4.1 Batarya Boyutlama \| WBS 9.3 Uçuş Prosedürü |
| **Standartlar** | Leishman §2 \| Glauert 1926 \| Prouty §2 \| Breguet uyarlaması \| NDARC §4.3 |

---

## 🔟 6 Adımlı Algoritma

### Adım 1: Drag Polari & Eğilme Açısı

```python
mu          = V_ff / (Omega * R)             # advance ratio
tan(alpha)  = D_parasite / (MTOW × g)        # iteratif
D_parasite  = 0.5 × rho × V² × f_D         # f_D ≈ 0.01 × MTOW^(2/3)
```

### Adım 2: Güç Bileşenleri (Glauert İnflow)

```python
# İndüklenmiş güç (Glauert iterasyonu):
lambda_iteratif → P_i = T × lambda × Omega × R

# Profil gücü:
P_pr  = n × rho × A × (Ω·R)³ × sigma×CD0/8 × (1 + 4.7×mu²)

# Parazit gücü:
P_para = 0.5 × rho × V³ × f_D      # ~ V³ ile büyür!

# Toplam:
P_total = P_i + P_pr + P_para
```

### Adım 3: V_max & V_opt

```python
# V hız taraması (0.5 m/s adımlarla):
for V in range(0, V_max_est):
    P_tot = compute_power(V)
    if P_tot > P_available or mu > 0.5: break

V_opt       = argmin(P_total)         # en uzun dayanım
V_best_range= argmax(W×V / P_total)   # en uzun menzil
V_max       = son geçerli V
```

### Adım 4: L/D Efektif

```python
L_over_D = MTOW × g × V_cruise / P_cruise   # multirotor L/D eşdeğeri
# Tipik multirotor: L/D 2–5 (uçak L/D 10–20 ile karşılaştırın)
```

### Adım 5: Menzil & Dayanım (Breguet Uyarlaması)

```python
range_km       = E_usable_Wh / P_cruise × V_cruise × 3.6     [km]
endurance_min  = E_usable_Wh / P_min × 60                     [min]
# E_usable = C_bat × 0.80  (%20 rezerv)
```

### Adım 6: Misyon Enerji Profili

| Faz | Süre | Güç | Enerji | % |
|-----|------|-----|--------|---|
| Kalkış (IGE→OGE) | 15 s | P_hover × 0.85 | E_to | 5–8% |
| Tırmanma | 30 s | P_hover × 1.20 | E_climb | 8–12% |
| **Sefer (V_cruise)** | t_cruise | **P_cruise** | **E_cruise** | **60–75%** |
| Bekleme/Loiter | t_loiter | P_hover | E_loiter | 5–15% |
| İniş | 20 s | P_hover × 0.70 | E_land | 3–5% |
| **Rezerv** | — | — | E_total × 0.20 | **20%** |

---

## 📊 Hız-Güç Eğrisi Örneği (MTOW=10kg, D=0.45m, n=6)

| V (m/s) | P_total (W) | L/D_eff | Not |
|---------|-------------|---------|-----|
| 0 | 1000 | 0 | Hover |
| 10 | 805 | 12.2 | **V_opt (min P)** |
| 20 | 1045 | 18.8 | Tipik V_cruise |
| 30 | 1900 | 15.5 | V_max yakını |
| 45 | 5145 | 8.6 | V_max |

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| — | V_cruise | ≤ V_max | Motor gücünü artır; DL düşür |
| — | range_km | ≥ range_req | Batarya kapasitesini artır |
| — | L/D_eff | ≥ 2.0 | Gövde fairing; parasite azalt |
| — | mu @ V_max | ≤ 0.50 | V_max kısıtla; retreating blade |

---

## forward_flight.json Şeması (Pydantic ForwardFlightResult)

```python
class ForwardFlightResult(BaseModel):
    V_cruise_ms:       float
    V_opt_ms:          float     # min güç hızı
    V_max_ms:          float
    V_best_range_ms:   float
    P_cruise_W:        float
    P_min_W:           float
    L_over_D:          float     # ≥ 2.0
    range_km:          float
    endurance_min:     float
    E_bat_req_Wh:      float     # WBS 4.1'e girdi
    energy_profile:    List[Dict]
    V_cruise_ok:       bool      # V_cruise ≤ V_max
    range_ok:          bool      # range ≥ range_req
    validation_passed: bool = True
```

---

*WBS 3.7 İleri Uçuş Analizi Detay Rehberi v4.0 — Nisan 2026*  
*6 Adım | Glauert İnflow + Breguet Menzil | V_max Tarama | 5 Faz Misyon Enerjisi | Pydantic ForwardFlightResult*
