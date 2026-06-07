# 🌡️ WBS 4.8 v1.0 — BATARYA TERMAL MONİTÖRİNG & GÜVENLİ DEŞARJ YÖNETİMİ [NEW-v4]

> **T_cell = T_amb + I²×R_int×R_th | 3 Kademeli Uyarı | I-Derate Eğrisi | OTA BMS | IEC 62619 §7**

> **v4 Notu (Mayıs 2026):** MultiCopter WBS v4.0'da yeni eklenen görev. mc_llm_v4.md tanımından üretilmiştir.

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 4.8 v1.0 [NEW-v4] |
| **Bağımlılık** | WBS 4.2 battery + WBS 4.4 bms + WBS 3.6 motor |
| **Çıktı** | bat_thermal.json |
| **Standart** | IEC 62619:2022 §7 | UN 38.3 §38.3.4 | DO-311A §2.4 |

---

## 🔬 Termal Model

```python
# mc_llm_v4 sabit parametreler:
R_TH_CELL = 0.05   # °C/W tipik LiPo hücresi (1. derece)

I_cell = I_total / n_parallel           # hücre başına akım
Q_gen  = I_cell ** 2 * R_int_Ohm       # ısı üretimi (W)
T_cell = T_amb + Q_gen * R_TH_CELL     # hücre sıcaklığı (°C)

# KK-BAT-THERMAL:
assert T_cell < T_max - 10.0, "KK-BAT-THERMAL FAIL"
```

---

## 🚦 3 Kademeli Uyarı Sistemi

```
T_warn   = T_max − 15°C    →  UYARI  : log kaydedilir; güç tam
T_limit  = T_max −  5°C    →  KISMA  : I_derate = 0.80 (%-20)
T_cutoff = T_max            →  KESİM  : deşarj tamamen durdurulur
```

### Kimya Başına Eşikler

| Kimya | T_max | T_warn | T_limit | T_cutoff |
|-------|-------|--------|---------|----------|
| LiPo | 60°C | 45°C | 55°C | 60°C |
| SSS Std/Prem | 65°C | 50°C | 60°C | 65°C |
| **ASS Pilot** | **55°C** | **40°C** | **50°C** | **55°C** |
| LiFePO4 | 70°C | 55°C | 65°C | 70°C |

---

## 📈 I-Derate Eğrisi

```python
def derate_factor(T, T_warn, T_limit, T_cutoff):
    if T < T_warn:
        return 1.0                                          # tam güç
    elif T < T_limit:
        return 1.0                                          # WARN: sadece log
    elif T < T_cutoff:
        frac = (T - T_limit) / (T_cutoff - T_limit)
        return round(1.0 - 0.20 * frac, 3)                 # lineer %20 kısma
    else:
        return 0.0                                          # CUTOFF: kes
```

---

## 🔄 OTA BMS Firmware Güncellemesi

`bat_thermal.json` içinde `OTA_fw_version` alanı tutulur. BMS eşikleri UART/CAN üzerinden güncellenebilir.
WBS 15.1 CI/CD pipeline entegrasyonu: yeni termal eşikler her build'de otomatik doğrulanır.

---

## ⚠️ Kritik Uyarılar

1. **ASS H₂S Riski:** Sülfid bazlı ASS elektroliti > 60°C'de H₂S gazı üretebilir → T_max = 55°C sınırı.
2. **R_th Belirsizliği:** R_TH_CELL = 0.05°C/W tahmin değeridir. Gerçek ölçüm için kalorimetri gerekir.
3. **Yüksek Ortam Sıcaklığı:** T_amb = 40°C ise tüm eşikler otomatik düşer → QQ bölgeleri daralır.

---

## ✅ Kabul Kriterleri

| Kriter | Limit |
|--------|-------|
| **KK-BAT-THERMAL** | T_cell ≤ T_max − 10°C @ max deşarj |
| 3 kademe uyarı | WARN / LIMIT / CUTOFF tanımlı |
| I_derate eğrisi | T_limit'te %20 kısma |
| IEC 62619 §7 | En az 2 kademe (WBS 4.8: 3 kademe) |

---

## ThermalResult Şeması

```python
class ThermalResult(BaseModel):
    chemistry:      str
    T_amb_C:        float
    T_cell_calc_C:  float
    T_warn_C:       float
    T_limit_C:      float
    T_cutoff_C:     float
    R_th_cell_CW:   float
    Q_gen_W:        float
    I_cell_A:       float
    I_derate_curve: Dict[str, float]   # {T_str: derate_factor}
    thermal_ok:     bool               # T_cell ≤ T_max − 10°C
    OTA_fw_version: str = 'v1.0.0'
    validation_passed: bool = True
```

---

*WBS 4.8 v1.0 [NEW-v4] — Mayıs 2026 | I²R Termal Model | 3 Kademe Uyarı | IEC 62619 §7*
