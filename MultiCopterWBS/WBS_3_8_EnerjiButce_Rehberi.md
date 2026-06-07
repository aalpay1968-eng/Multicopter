# ⚡ WBS 3.8 — ENERJİ BÜTÇE & AŞAMA 3 KAPANIŞI

> **Misyon Enerji Kapatması | phase_3_aero.json | KK-3 Dayanım ≥ req×1.20**  
> Breguet | NDARC §4 | Pydantic EnergyBudgetResult | AŞAMA 3 VALIDASYON

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 3.8 |
| **Faz** | AŞAMA 3 — İtki Sistemi & BEMT Analizi  |  **AŞAMA 3 KAPANIŞI** |
| **Görev** | Enerji Bütçe & AŞAMA 3 Validasyonu |
| **Girdi** | WBS 3.1–3.7 tüm JSON çıktıları (7 dosya) + `requirements.json` |
| **LLM Script** | `energy_budget.py` |
| **Çıktı** | `energy_budget.json` + `phase_3_aero.json`: E_bat_min_Wh, KK_summary, phase_3_complete |
| **Kabul Kriteri** | KK-3: dayanım ≥ req×1.20 \| KK-1/4/5 PASS \| Pydantic PASS \| phase_3_complete=True |
| **Sonraki WBS** | WBS 4.1 Batarya Boyutlama (E_bat_min_Wh) \| WBS 7.1 6-DOF \| WBS 14.6 SwFMEA |
| **Standartlar** | NDARC §4 \| Breguet \| DO-178C §6.3 \| JARUS SORA OSO#07 |

---

## 🏗️ WBS 3.8'in Rolü

```
WBS 3.1 hover.json         ──┐
WBS 3.2 bemt.json          ──┤
WBS 3.3 ground_effect.json ──┤
WBS 3.4 coax.json          ──┤──► energy_budget.py ──► phase_3_aero.json
WBS 3.5 prop_match.json    ──┤                               │
WBS 3.6 noise.json         ──┤                 phase_3_complete = True?
WBS 3.7 forward_flight.json──┘                               │
                                             YES: AŞAMA 4'e geç ✅
                                             NO:  İlgili WBS'e geri dön ❌
```

---

## 📊 Misyon Enerji Bütçesi

| Faz | Güç | Süre | Enerji | % |
|-----|-----|------|--------|---|
| Kalkış (IGE→OGE) | P_hover × 0.85 | 15 s | E_to | 5–8% |
| Tırmanma | P_hover × 1.20 | 30 s | E_climb | 8–12% |
| **Sefer** | **P_cruise** | **t_cruise** | **E_cruise** | **60–75%** |
| Bekleme/Loiter | P_hover | t_loiter | E_loiter | 5–15% |
| İniş | P_hover × 0.70 | 20 s | E_land | 3–5% |
| Aviyonik+Payload | P_avion + P_PL | t_total | E_elec | 2–4% |
| **Rezerv (%20)** | — | — | **E_misyon×0.25** | **20%** |
| **E_bat_min** | — | — | **E_misyon / 0.80** | **100%** |

```python
E_bat_min = E_misyon_total / 0.80         # %20 rezerv zorunlu (KK-3)
# Zemin etkisi tasarrufu düşülür: E_ge_saving_Wh
t_endurance = (E_bat_min × 0.80) / P_hover × 60   # [min]
# KK-3: t_endurance >= t_hover_req × 1.20
```

---

## 🔑 AŞAMA 3 KK Kontrol Matrisi

| KK | Parametre | Limit | Kaynak | AŞAMA 4 Etkisi |
|----|-----------|-------|--------|----------------|
| **KK-1** | T/W @ hover | ≥ 2.0 | hover.json | BLOKE |
| **KK-3** | Dayanım | ≥ req×1.20 | forward_flight.json | BLOKE |
| **KK-4** | DL | ≤ 300 N/m² | hover.json | BLOKE |
| **KK-5** | FM_actual + FM_coax | ≥ 0.60 | bemt + coax | BLOKE |
| **KK-13** | Yaw \|Q\| | ≤ 0.01 N·m | bemt.json | BLOKE |
| Gürültü | L_Aeq | ≤ limit | noise.json | UYARI |
| Menzil | range | ≥ req | forward_flight.json | UYARI |
| V_max | V_cruise | ≤ V_max | forward_flight.json | BLOKE |

---

## phase_3_aero.json Yapısı

```python
class EnergyBudgetResult(BaseModel):
    E_misyon_Wh:       float    # ge=0
    E_elec_Wh:         float    # ge=0
    E_ge_saving_Wh:    float    # zemin etkisi tasarrufu
    E_misyon_total_Wh: float    # gt=0
    E_bat_min_Wh:      float    # gt=0  → WBS 4.1'e
    t_endurance_min:   float    # KK-3 kontrolü
    t_hover_req_min:   float
    KK1_pass:          bool
    KK3_pass:          bool     # dayanım ≥ req×1.20
    KK4_pass:          bool
    KK5_pass:          bool
    KK13_pass:         bool
    Vmax_pass:         bool
    range_pass:        bool
    noise_pass:        bool
    phase_3_complete:  bool     # tüm BLOKE KK PASS ise True
    kk_summary:        Dict[str, str]
    validation_passed: bool = True

# phase_3_aero.json = {hover, bemt, ground, coax, prop, noise, forward, energy}
```

---

## 🔗 WBS Bağlantıları (AŞAMA 3 → AŞAMA 4)

```
phase_3_aero.json (WBS 3.8)
    │
    ├── E_bat_min_Wh ──► WBS 4.1 battery_size.py
    ├── kk_summary   ──► WBS 14.6 SwFMEA (risk senaryoları)
    ├── RPM_hover    ──► WBS 3.9 motor_select.py
    └── phase_3_complete=True ──► AŞAMA 4 geçiş onayı
```

---

*WBS 3.8 Enerji Bütçe & AŞAMA 3 Kapanışı Detay Rehberi v4.0 — Nisan 2026*  
*AŞAMA 3 KAPANIŞI | 7 JSON → phase_3_aero.json | KK-3 Dayanım ≥ req×1.20 | Pydantic EnergyBudgetResult*
