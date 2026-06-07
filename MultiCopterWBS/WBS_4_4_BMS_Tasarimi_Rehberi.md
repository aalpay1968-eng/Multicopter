# 🛡️ WBS 4.4 v1.0 — BMS (BATARYA YÖNETİM SİSTEMİ) TASARIMI

> **OVP | UVP | OCP | OTP | SCP | Pasif/Aktif Balans | DroneCAN/UART | IEC 62619**

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 4.4 v1.0 |
| **Bağımlılık** | WBS 4.2 battery.json + WBS 4.3 charger.json + WBS 3.6 motor.json |
| **Çıktı** | bms.json |
| **Standart** | IEC 62619:2022 §7 | DO-311A | UN 38.3 |

---

## 🔬 5 Koruma Fonksiyonu (IEC 62619 Zorunlu)

| # | Koruma | Açıklama | LiPo/SSS Eşiği | ASS Eşiği | Tepki |
|---|--------|----------|----------------|-----------|-------|
| 1 | **OVP** | Aşırı voltaj | 4.25 V/hücre | 4.25 V | Şarjı kes |
| 2 | **UVP** | Düşük voltaj | 2.95 V/hücre | 3.05 V | Deşarjı kes |
| 3 | **OCP** | Aşırı akım | I_max × 1.10 | I_max × 1.10 | ≤ 5 ms kes |
| 4 | **OTP** | Aşırı sıcaklık | 60°C | **55°C** | Derate → kes |
| 5 | **SCP** | Kısa devre | < 200 µs | < **100 µs** | Anında FET kes |

---

## 🔟 5 Adımlı Algoritma

### Adım 2: Koruma Eşikleri

```python
CHEM_PARAMS = {
    'LiPo':  {'V_max':4.20,'V_min':3.00,'T_max':60},
    'SSS':   {'V_max':4.22,'V_min':3.00,'T_max':65},
    'ASS':   {'V_max':4.20,'V_min':3.05,'T_max':55},
    'LiFePO4':{'V_max':3.65,'V_min':2.50,'T_max':70},
}
p = CHEM_PARAMS[chemistry]
OVP_V = p['V_max'] + 0.05    # hücre başına
UVP_V = p['V_min'] - 0.05
OCP_A = I_max_total * 1.10
OTP_C = min(p['T_max'] + 5, 65)  # ASS: min 55°C
```

### Adım 3: Balans Tipi

```python
# Büyük paket ve SSS/ASS → aktif balans
balance_type = 'active' if (S > 8 or chemistry in ['SSS','SSS_prem','ASS']) else 'passive'
```

### Adım 4: Haberleşim

```python
# SAIL ≥ III → DroneCAN (güvenilirlik); aksi → UART/MAVLink
comm = 'DroneCAN' if SAIL_level in ['SAIL-III','SAIL-IV'] else 'UART'
```

---

## 📡 Haberleşim Protokolü Karşılaştırması

| Protokol | Hız | Gürültü Dayanımı | PX4 Destek | Öneri |
|----------|-----|-----------------|-----------|-------|
| **DroneCAN** | 1 Mbit/s | Çok Yüksek | Native | ⭐ Tercih |
| UART/MAVLink | 115200 bps | Orta | Evet | Basit kurulum |
| I²C | 400 kbit/s | Düşük | Evet | Kısa mesafe |
| CAN 2.0 | 1 Mbit/s | Yüksek | Evet | DroneCAN altyapısı |

---

## ⚠️ SSS/ASS BMS Özel Gereksinimleri

- **SSS:** Aktif balans tercih; `balance_type = 'active'`; üretici SSS BMS spesifikasyonu kontrol et.
- **ASS:** OTP eşiği 55°C (daha kısıtlı); SCP tepki < 100 µs; özel ASS BMS donanımı.
- **H₂S Riski:** Sülfid bazlı ASS elektroliti nem temasında H₂S üretir → risk_flags'e eklenir → WBS 14.6 SwFMEA.

---

## ✅ Kabul Kriterleri

| Kriter | Limit | İhlal |
|--------|-------|-------|
| 5 koruma aktif | protection_count = 5 | IEC 62619 ihlali |
| OVP > UVP | Mantık kontrolü | Pydantic hata |
| SCP tepki | LiPo/SSS ≤ 200 µs | FET seçimi |
| DroneCAN | SAIL ≥ III | WBS 14.6 risk |

---

## BMSResult Şeması

```python
class BMSResult(BaseModel):
    chemistry:       str
    cell_count:      int
    OVP_V:           float
    UVP_V:           float
    OCP_A:           float
    OTP_C:           float
    SCP_flag:        bool
    SCP_response_us: int
    balance_type:    str   # 'passive' | 'active'
    I_balance_mA:    int
    comm:            str   # 'DroneCAN' | 'UART' | 'I2C'
    weight_g:        int
    protection_count: int = 5
    validation_passed: bool = True
```

---

*WBS 4.4 v1.0 — Mayıs 2026 | 5 Koruma Fonksiyonu | SSS/ASS BMS | IEC 62619:2022 §7*
