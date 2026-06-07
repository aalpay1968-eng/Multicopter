# ⚖️ WBS 1.3 — MEVZUAT SINIFI & SORA RİSK DEĞERLENDİRMESİ

> **JARUS SORA v2.5 sürecini LLM ajanı aracılığıyla otomatik yürütür.**
> 10 Adım | GRC Tablosu | ARC Belirleme | SAIL Matrisi | 24 OSO | EASA/FAA/SHGM

---
## 🔟 10 Adımlı SORA Süreci Özeti

### Adım 1: ConOps Belgeleme
**Girdi:** `mission_profile.json` → **Çıktı:** `conops.json: flight_geography, buffer_zone, UA_type, ops_type, environment`
**Standart:** JARUS SORA v2.5 §2.2.3
```python
LLM mission_profile.json'u okur → ConOps şablonunu doldurur:
```

### Adım 2: Başlangıç GRC (iGRC) Belirleme
**Girdi:** `conops.json: UA_max_dim, population_density, V_max` → **Çıktı:** `iGRC_value: 1–10 (tam sayı)`
**Standart:** JARUS SORA v2.5 §2.2.4 + Annex F
```python
iGRC = GRC_TABLE[max_dim_m][population_density]
```

### Adım 3: Nihai GRC Belirleme (Azaltmalar)
**Girdi:** `iGRC [Adım 2], mitigation_flags: M1, M2` → **Çıktı:** `final_GRC: 1–7`
**Standart:** JARUS SORA v2.5 §2.2.5 + Annex B + Tablo 5
```python
final_GRC = iGRC - M1_credit - M2_credit
```

### Adım 4: Başlangıç ARC (iARC) Belirleme
**Girdi:** `conops.json: airspace_class, altitude_AGL, airport_dist_km` → **Çıktı:** `iARC: a, b, c, d`
**Standart:** JARUS SORA v2.5 §2.3.1 + Annex C
```python
iARC = ARC_TABLE[airspace_class][flight_type][altitude]
```

### Adım 5: Stratejik Azaltma → Artık ARC
**Girdi:** `iARC [Adım 4], strategic_mitigations[], airspace_agreements` → **Çıktı:** `residual_ARC: a, b, c, d`
**Standart:** JARUS SORA v2.5 §2.3.2 + Annex C
```python
residual_ARC = strategic_mitigation(iARC)
```

### Adım 6: Taktik Azaltma (TMPR)
**Girdi:** `residual_ARC [Adım 5], SAIL (Adım 7)` → **Çıktı:** `TMPR_level: Low/Medium/High, DAA_required, ATC_coord`
**Standart:** JARUS SORA v2.5 §2.3.3 + Tablo 6
```python
TMPR seviyesi = SAIL'e göre belirlenir (Adım 7 sonrası rafine)
```

### Adım 7: SAIL Belirleme
**Girdi:** `final_GRC [Adım 3], residual_ARC [Adım 5]` → **Çıktı:** `SAIL: I–VI (Romen rakamı)`
**Standart:** JARUS SORA v2.5 §2.4 + Tablo 7
```python
SAIL = SAIL_MATRIX[final_GRC][residual_ARC]
```

### Adım 8: Kapsam (Containment) Gereksinimleri
**Girdi:** `SAIL [Adım 7], alt_AGL, V_max, UA_dim` → **Çıktı:** `containment.json: level, buffer_zone_m, d_ballistic_m, geofence_required`
**Standart:** JARUS SORA v2.5 §2.5 + Annex E §4
```python
containment_level = f(SAIL, UA_dim, population_density)
```

### Adım 9: OSO Ataması (24 OSO)
**Girdi:** `SAIL [Adım 7], operation_profile` → **Çıktı:** `oso_compliance.json: {oso_01: {required: M, status: compliant}, ...}`
**Standart:** JARUS SORA v2.5 §2.6 + Annex E + Tablo 14
```python
oso_robustness = OSO_TABLE[oso_number][SAIL_level]
```

### Adım 10: Kapsamlı Güvenlik Portfolyosu
**Girdi:** `Adımlar 1-9 tüm çıktıları` → **Çıktı:** `safety_portfolio.json: complete=True, submitted=False, authority_ref`
**Standart:** JARUS SORA v2.5 §2.7 + Annex A
```python
safety_portfolio = compile_evidence(adımlar 1-9)
```

---
## 📊 iGRC Tablosu (SORA v2.5 Annex F)

| Nüfus Yoğunluğu | <1 m | 1–3 m | 3–8 m | 8–20 m | >20 m |
|-----------------|------|-------|-------|--------|-------|
| Seyrek (<10 kişi) / Kontrolsüz uzak | 1 | 2 | 3 | 4 | 5 |
| Az yoğun (10–50) / Kırsal | 2 | 3 | 4 | 5 | 6 |
| Orta (50–500) / Banliyö | 3 | 4 | 5 | 6 | 7 |
| Yoğun (500–5000) / Kentsel | 4 | 5 | 6 | 7 | 8 |
| Çok yoğun (>5000) / Kalabalık kentsel | 5 | 6 | 7 | 8 | 9 |
| Kalabalık etkinlik (>100.000/km²) | 6 | 7 | 8 | 9 | 10 |

> ⚠️ V_max > 35 m/s → iGRC +1 | final_GRC > 7 → SORA kapsam dışı → Certified

---
## 📐 SAIL Matrisi (SORA v2.5 Tablo 7)

| Final GRC | ARC-a | ARC-b | ARC-c | ARC-d | DAL |
|-----------|-------|-------|-------|-------|-----|
| GRC 1–2 | I | II | III | IV | DAL-D |
| GRC 3–4 | II | III | III | IV | DAL-D |
| GRC 5 | III | III | IV | V | DAL-C |
| GRC 6 | III | III | V | VI | DAL-B |
| GRC 7 | IV | IV | V | VI | DAL-B/A |

---
## 📋 24 OSO — Kısa Referans

| OSO | Konu | SAIL III | WBS Bağlantısı |
|-----|------|---------|----------------|
| `OSO#01` | Operatör yetkinliği kanıtlı | M | WBS 12.4 operatör eğitim materyali |
| `OSO#02` | UAS yetkili üretici tarafından üretilmiş | M | WBS 12.1 BOM yönetimi; tedarikçi kalifik |
| `OSO#03` | UAS yetkili kişi tarafından bakımı yapıl | M | WBS 12.4 bakım planı; TBO hesabı |
| `OSO#04` | UAS ticari yapım standardı ile üretilmiş | M | WBS 12.2 montaj prosedürü; WBS 12.3 QA |
| `OSO#05` | UAS tasarım ve imalat süreçleri için güv | M | WBS 11.7 DO-178C; WBS 11.3 DO-160G; WBS  |
| `OSO#06` | C3 linki yeterli performans ve dayanıklı | M | WBS 8.2 C2 datalink; WBS 8.3 güvenlik; W |
| `OSO#07` | UAS konfigürasyon uyumu kontrol edilmiş | M | WBS 9.5 preflight otomasyon; WBS 7.9 FW  |
| `OSO#08` | Operasyonel prosedürler ve ERP belgelenm | M | WBS 7.8 geofence+RTL; WBS 9.5 preflight |
| `OSO#09` | Uzaktan pilot eğitim almış | M | WBS 12.4 operatör eğitim müfredatı |
| `OSO#10` | UAS olumsuz koşullara karşı tasarlanmış | M | WBS 6.6 çevre koruma; WBS 11.3 çevre tes |
| `OSO#11` | Harici destek hizmetleri (UTM/GNSS) yete | L | WBS 8.6 UTM; WBS 7.7 EKF (GNSS kaybı sen |
| `OSO#12` | GNSS hassasiyeti operasyon için yeterli | L | WBS 9.6 compass-mot; WBS 8.1 GNSS tipi |
| `OSO#13` | Hava durumu koşulları operasyon öncesi k | L | WBS 9.5 preflight checklist; hava durumu |
| `OSO#14` | Operatör riskler konusunda farkında | L | WBS 12.4 eğitim materyali; WBS 14.6 Bow- |
| `OSO#15` | Çevre/güvenlik tehditlerinin tespiti eği | L | WBS 12.4 eğitim; WBS 14.6 SwFMEA |
| `OSO#16` | Ekip koordinasyon prosedürleri mevcut | L | WBS 12.4 ekip eğitimi; crew_size [WBS 1. |
| `OSO#17` | Operatör uygun fiziksel/zihinsel durumda | L | WBS 12.4 operatör kılavuzu |
| `OSO#18` | Otomasyon sürprizlerine karşı eğitim | L | WBS 12.4 + WBS 7.9 FW config dokümantasy |
| `OSO#19` | Sağlık ve güvenlik protokolleri mevcut | L | WBS 12.4 güvenlik bölümü |
| `OSO#20` | İnsan faktörleri tasarımda dikkate alınm | N/A | WBS 8.5 GCS kurulum; HMI tasarımı |
| `OSO#21` | Olumsuz meteorolojik koşullar için prose | M | WBS 9.5 preflight; hava limitleri [WBS 1 |
| `OSO#22` | GNSS sinyal bozulması için prosedür | M | WBS 7.5 irtifa kontrolcüsü; WBS 7.7 EKF |
| `OSO#23` | Gece/düşük görüş koşulları için prosedür | L | ops_time [WBS 1.1]; EASA gece operasyon |
| `OSO#24` | UAS olumsuz çevre koşulları için tasarla | M | WBS 11.3 DO-160G çevre testi; WBS 6.6 IP |

---
## 🐍 Hızlı Kod Referansı

```python
# sora_assessment.py — Temel akış
iGRC        = IGRC_TABLE[pop_density][UA_dim_class]  # Adım 2
final_GRC   = iGRC - M1_credit - M2_credit           # Adım 3
iARC        = determine_iARC(airspace, alt, airport)  # Adım 4
residual_ARC= strategic_mitigation(iARC)              # Adım 5
SAIL        = SAIL_MATRIX[final_GRC][residual_ARC]    # Adım 7
buffer_m    = V_h * sqrt(2*alt/g) * 1.5              # Adım 8
oso_reqs    = OSO_REQUIREMENTS[SAIL]                  # Adım 9
# → regulation.json (Pydantic RegulationResult ile doğrulanmış)
```

---
*WBS 1.3 SORA v2.5 Detay Rehberi — Nisan 2026 | 10 Adım | 24 OSO | GRC+SAIL Matrisi*