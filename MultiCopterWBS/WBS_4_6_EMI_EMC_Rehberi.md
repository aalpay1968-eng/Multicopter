# 📡 WBS 4.6 v1.0 — EMI/EMC ANALİZİ & GÜRÜLTÜ AZALTMA

> **ESC Harmonikleri | GPS SNR ≥ 35 dB | Ferrit Boncuk | DO-160G §21 | RTCA DO-316A**

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 4.6 v1.0 |
| **Bağımlılık** | WBS 3.6 motor + WBS 3.7 ESC + WBS 4.5 PDB + WBS 2.4 geometri |
| **Çıktı** | emi.json |
| **Standart** | DO-160G §21 | RTCA DO-316A | FCC Part 15 |

---

## 🔟 5 Adımlı Algoritma

### Adım 1: ESC Harmonik Hesabı

```python
f_sw_Hz   = esc_json['switching_freq_kHz'] * 1000
harmonics = [n * f_sw_Hz for n in range(1, 8)]

GPS_BANDS = [1575.42e6, 1227.60e6, 1176.45e6]  # L1, L2, L5 Hz
GPS_margin = min(abs(gps_f - h) for gps_f in GPS_BANDS for h in harmonics)
# Kriter: GPS_margin ≥ 100 MHz
```

### Adım 2: GPS SNR Analizi

```python
# SNR kaybı: 1/r² modeli
SNR_loss_dB = 20 * log10(REF_DIST / d_GPS_motor_mm)
GPS_SNR = GPS_SNR_open - SNR_loss
# GPS_SNR ≥ 35 dB → PASS
```

### Adım 3: Mitigation Kararı

```python
if GPS_SNR < 38:
    shielding_type = 'aluminium_shield_and_ferrite'
elif GPS_SNR < 40:
    shielding_type = 'ferrite_only'
else:
    shielding_type = 'none'
```

---

## 📊 GPS Gürültü Kaynakları & Azaltma

| Kaynak | Min Mesafe | SNR Kaybı | Azaltma |
|--------|-----------|-----------|---------|
| ESC anahtarlama | 100 mm | 1–3 dB | Ferrit boncuk + kalkan |
| PDB güç kablosu | 150 mm | 2–5 dB | AWG twist çift |
| LiPo ani deşarj | 100 mm | 1–2 dB | 470µF low-ESR filtre |
| Video TX (5.8GHz) | 120 mm | 3–8 dB | GPS kalkan + ayrım |

---

## 🔧 Azaltma Yöntemleri

```
GPS SNR Bütçesi (örnek):
  Açık alan SNR:          45 dB
  ESC harmonik kaybı:    −2 dB  (ferrit ile azaltılmış)
  Kablo gürültüsü:       −2 dB  (twist-pair ile)
  Video TX girişimi:     −3 dB  (kalkan ile azaltılmış)
  ─────────────────────────────
  Net GPS SNR:            38 dB  ✅ ≥ 35 dB
```

**Ferrit Boncuk:** BN-43-202 — her ESC güç girişine; 1–500 MHz bant azaltma.
**GPS Kalkanı:** Alüminyum kutu GPS modülü altına; 30–50 dB azaltma.

---

## ✅ Kabul Kriterleri

| Kriter | Limit |
|--------|-------|
| GPS SNR | ≥ 35 dB |
| ESC → GPS bant ayrımı | ≥ 100 MHz |
| DO-160G RE102 | Cat. B seviyesi altında |
| Kalkan tipi | Belirlenmiş |

---

## EMIResult Şeması

```python
class EMIResult(BaseModel):
    f_sw_kHz:             float
    switching_harmonics:  List[int]
    GPS_band_margin_MHz:  float
    GPS_band_ok:          bool
    GPS_SNR_dB:           float
    GPS_SNR_ok:           bool
    GPS_separation_mm:    int
    shielding_type:       str
    ferrite_spec:         str
    RE102_estimated_ok:   bool
    validation_passed:    bool = True
```

---

*WBS 4.6 v1.0 — Mayıs 2026 | GPS SNR ≥ 35dB | DO-160G §21 | RTCA DO-316A*
