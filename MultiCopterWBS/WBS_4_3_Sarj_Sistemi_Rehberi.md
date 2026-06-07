# 🔌 WBS 4.3 v1.0 — ŞARJ SİSTEMİ & BALANS ŞARJ PROSEDÜRÜ

> **CC-CV Profili | ΔV ≤ 5 mV | Şarj Hızı ≤ 2C | Depolama Voltajı | SSS/ASS Özel Profil**

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 4.3 v1.0 |
| **Bağımlılık** | WBS 4.2 battery.json + WBS 4.1 battery_chem.json |
| **Çıktı** | charger.json |
| **Standart** | IEC 62619 | UN 38.3 | IEEE 1725 |

---

## 🔬 Şarj Profili Referans Tablosu

| Kimya | V_cell_max | V_storage | C_max_charge | Balans ΔV | Özel Not |
|-------|-----------|-----------|-------------|-----------|----------|
| LiPo | 4.20 V | 3.80 V | 2C | ≤ 5 mV | Standart CC-CV |
| LiHV | 4.35 V | 3.85 V | 2C | ≤ 5 mV | 4.35V dikkat |
| Li-Ion | 4.20 V | 3.70 V | 1C | ≤ 5 mV | 0.5C önerilir |
| SSS Std. | 4.20 V | 3.80 V | 1.5C | ≤ 5 mV | Üretici protokolü |
| SSS Prem. | 4.25 V | 3.80 V | 1C | **≤ 3 mV** | Aktif balans |
| **ASS Pilot** | 4.20 V | 3.75 V | **0.5C (!)** | ≤ 5 mV | Özel lab cihazı |
| LiFePO4 | 3.65 V | 3.40 V | 2C | ≤ 10 mV | Geniş tolerans |

---

## 🔟 5 Adımlı Algoritma

### Adım 2: Şarj Gerilimi & Akımı

```python
V_charge     = S * V_cell_max
C_rate_chg   = min(C_chg_max, chemistry_params['C_chg_safe'])
I_charge_A   = C_rate_chg * (C_mAh / 1000)

# Şarj süresi: CC 80% + CV 20%
t_CC_min   = 0.80 * (C_mAh/1000) / I_charge_A * 60
t_CV_min   = 0.20 * t_CC_min
t_total    = t_CC_min + t_CV_min
```

### Adım 3: Balans Şarj

```python
# Balans stratejisi
dV_target_mV = {
    'LiPo':     5,
    'SSS':      5,
    'SSS_prem': 3,   # daha hassas
    'ASS':      5,
}.get(chemistry, 5)

# n_series > 8 veya SSS/ASS → aktif balans tercih
balance_type = 'active' if (S > 8 or chemistry in ['SSS','ASS']) else 'passive'
```

### Adım 4: Depolama Voltajı

```python
V_storage_cell = {
    'LiPo': 3.80, 'LiHV': 3.85, 'Li-Ion': 3.70,
    'SSS': 3.80, 'ASS': 3.75, 'LiFePO4': 3.40
}.get(chemistry, 3.80)
V_storage_pack = S * V_storage_cell
```

---

## ⚠️ ASS Şarj Uyarıları

1. **Yavaş şarj:** ASS pilot 0.5C → 6S5000mAh için 120+ dakika.
2. **Minimum sıcaklık:** 15°C altında ASS şarj etme; elektrolit kondüktivite düşer.
3. **Özel cihaz:** 2026 itibarıyla ticari ASS şarj cihazı mevcut değil → üretici servisi.
4. **ΔV takibi:** ASS'de hücre dengesizliği erken uyarıdır; BMS ile anlık izle (WBS 4.4).

---

## ✅ Kabul Kriterleri

| Kriter | Limit | İhlal Eylemi |
|--------|-------|--------------|
| ΔV_balance | ≤ 5 mV (SSS Prem: ≤ 3 mV) | Balans tipi yükselt (pasif→aktif) |
| Şarj hızı | ≤ 2C (ASS: ≤ 0.5C) | C_rate_chg düşür |
| Depolama V | 3.80 V/hücre (ASS: 3.75) | Depolama prosedürü uygula |
| Şarj T_min | LiPo/SSS: 0°C | Ortam sıcaklığını kontrol et |

---

## ChargerResult Şeması

```python
class ChargerResult(BaseModel):
    chemistry:       str
    charge_rate_C:   float
    V_charge_V:      float
    I_charge_A:      float
    balance_dV_mV:   float
    storage_V_pack:  float
    storage_V_cell:  float
    charge_time_min: float
    charger_model:   str
    profile_type:    str = 'CC-CV'
    dV_ok:           bool
    rate_ok:         bool
    validation_passed: bool = True
```

---

*WBS 4.3 v1.0 — Mayıs 2026 | CC-CV Şarj Profili | SSS/ASS Özel Kurallar | IEC 62619*
