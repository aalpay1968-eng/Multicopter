# 🔊 WBS 3.6 — GÜRÜLTÜ ANALİZİ (Rotor Akustik)

> **Rotasyonel + Geniş Bant + Toplam SPL | Mesafeye Göre Azalma | EASA U-Space**  
> Gutin 1948 | Ffowcs Williams-Hawkings | ISO 3744 | Pydantic NoiseResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 3.6 |
| **Faz** | AŞAMA 3 — İtki Sistemi & BEMT Analizi |
| **Görev** | Rotor Akustik & Gürültü Analizi |
| **Girdi** | `prop_match.json` (WBS 3.5) + `bemt.json` (WBS 3.2) + `requirements.json` |
| **LLM Script** | `noise_analysis.py` |
| **Çıktı** | `noise.json`: SPL_1m_dB, SPL_observer_dB, L_Aeq_dBA, f_BPF_Hz, noise_pass, reduction_tips[] |
| **Kabul Kriteri** | L_Aeq ≤ L_limit (EASA U-Space: 65 dB(A) @ 50m) \| Ma_tip ≤ 0.85 \| Pydantic PASS |
| **Sonraki WBS** | WBS 3.7 İleri Uçuş \| WBS 1.3 SORA gürültü beyanı \| WBS 9.3 Operasyonel Kısıtlar |
| **Standartlar** | Gutin 1948 \| Brooks et al. 1989 \| ISO 3744:2010 \| EASA U-Space 2022 \| WHO 2018 |

---

## 🔟 5 Adımlı Algoritma

### Adım 1: Blade Passing Frequency (BPF)

```python
f_BPF  = n_blades × RPM / 60           # Hz — blade geçiş frekansı
Ma_tip = V_tip / a_ses                  # a_ses ≈ 343 m/s @ 20°C
# Harmonikler: f_n = n × f_BPF (n=1,2,3...)
# Rahatsız edici aralık: 1000–4000 Hz
# Kısıt: Ma_tip ≤ 0.85 (transonic sınır)
```

### Adım 2: Rotasyonel Gürültü (Gutin 1948)

```python
# Gutin ampirik yaklaşım (1m referans, hover):
SPL_rot   = 20×log10(T × n_b × Ma_tip²) + K_geom    # K_geom ≈ 50 dB
SPL_thick = 20×log10(t/c × Ma_tip²) + 40.0          # kalınlık gürültüsü
SPL_rotational = 10×log10(10^(SPL_rot/10) + 10^(SPL_thick/10))
```

### Adım 3: Geniş Bant Gürültü (Brooks 1989)

```python
# Türbülans kaynaklı broadband (ampirik):
SPL_broadband = 58.5 + 50×log10(V_tip/100) + 10×log10(chord/0.10)
# V_tip'in 5. kuvvetiyle orantılı → V_tip azaltma en etkili önlem!
```

### Adım 4: Toplam SPL & Mesafe Azalması

```python
SPL_single_1m = 10×log10(10^(SPL_rot/10) + 10^(SPL_bb/10))
SPL_total_1m  = SPL_single_1m + 10×log10(n_rotors) + 3.0  # zemin yansıması

# Mesafe azalması + hava yutulması:
SPL_obs = SPL_1m - 20×log10(r) - alpha_atm×r    # alpha ~ 0.2 dB/m @ 1kHz

# A-ağırlıklandırma (ISO 61672):
L_Aeq = SPL_obs + A_weight(f_BPF)
```

### Adım 5: Limit Kontrolü & Azaltma Önerileri

```python
noise_pass = L_Aeq <= L_limit_dB
if not noise_pass:
    → otomatik reduction_tips[] üret
```

---

## 📊 Tipik SPL Değerleri

| Platform | V_tip (m/s) | Ma_tip | f_BPF (Hz) | SPL@1m (dB) | Durum |
|----------|-------------|--------|------------|-------------|-------|
| DJI Mini 4 | 115 | 0.336 | 488 | 74 | Sessiz |
| DJI Mavic 3 | 130 | 0.379 | 344 | 78 | Kabul |
| Hex kargo | 145 | 0.423 | 243 | 82 | Dikkat |
| GRIFF-135 | 155 | 0.452 | 164 | 86 | Yüksek |
| 3 kanat opt. | 145 | 0.423 | 364 | 81 | Azaltılmış |
| Ducted fan | 140 | 0.408 | 595 | 77 | Sessiz+ |

---

## 🔇 Gürültü Azaltma Stratejileri

| Strateji | dB Azalma | Etki | Maliyet |
|----------|-----------|------|---------|
| V_tip -10% (D artır) | ~5 dB | Çok Büyük | Düşük |
| 2→3 kanat | ~3 dB | Orta | Orta |
| Swept/raked uç | ~3 dB | Orta | Orta |
| Ducted fan/shroud | ~8 dB | Çok Büyük | Yüksek |
| İrtifa artırma (2×) | ~6 dB | Büyük | Yok |
| Düşük DL konfigürasyonu | ~6 dB | Çok Büyük | Orta |

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| EASA U-Space | L_Aeq @ 50m | ≤ 65 dB(A) | V_tip azalt; kanat sayısını artır |
| — | Ma_tip | ≤ 0.85 | RPM azalt; D artır |
| — | noise_pass | True | reduction_tips uygula |

---

## noise.json Şeması (Pydantic NoiseResult)

```python
class NoiseResult(BaseModel):
    V_tip_ms:            float
    Ma_tip:              float    # ≤ 0.85
    RPM_hover:           float
    n_blades:            int
    n_rotors:            int
    f_BPF_Hz:            float
    SPL_rotational_dB:   float
    SPL_broadband_dB:    float
    SPL_total_1m_dB:     float
    r_observer_m:        float
    SPL_observer_dB:     float
    A_correction_dB:     float
    L_Aeq_dBA:           float    # ≤ L_limit
    L_limit_dBA:         float
    noise_pass:          bool
    excess_dB:           float
    reduction_tips:      List[str]
    validation_passed:   bool = True
```

---

*WBS 3.6 Gürültü Analizi Detay Rehberi v4.0 — Nisan 2026*  
*5 Adım | Gutin 1948 + Brooks 1989 | BPF | L_Aeq | EASA U-Space 65 dB(A) | Pydantic NoiseResult*
