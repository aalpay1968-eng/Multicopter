# 🚁 MULTİCOPTER WBS v4.0 — DELTA GÜNCELLEME TALİMATI

> **v4.0 = v3.0 + Bu dosya.** Önce `mc_llm_v3.md` talimatlarını uygula, sonra bu delta güncellemeleri ekle.
> v4'te eklenen: **+13 yeni görev** | **+3 STD fix** | **+WBS 15 (CI/CD fazı)**

---
## 🆕 v4 YENİ GÖREVLERİN ÖZET TALİMATI

### `WBS 4.8` Batarya Termal Monitöring [NEW-v4]
**Script:** `bat_thermal.py`
```python
# T_cell = T_amb + I²×R_int×R_th_cell
# Uyarı seviyeleri: WARN@T_max-15°C, LIMIT@T_max-5°C, CUTOFF@T_max
R_th_cell = 0.05   # °C/W tipik LiPo hücre
I_hover_per_cell = I_total / (battery['P'] * battery['S'])
T_cell = T_amb + (I_hover_per_cell**2 * motor['R_int_Ohm'] * R_th_cell)
assert T_cell < battery_chem['T_max_C'] - 10, "KK-BAT-THERMAL FAIL"
```
**Çıktı:** `bat_thermal.json` | **Kriter:** T_cell ≤ T_max - 10°C | **Std:** IEC 62619 §7

---
### `WBS 7.10` Dual IMU Redundancy [NEW-v4]
**Script:** `dual_imu.py`
```python
# IMU tutarsızlık tespiti
att_diff_deg = abs(imu1_att_deg - imu2_att_deg)
if att_diff_deg > 0.5:  # failover eşiği
    active_imu = "secondary"
    log_event("IMU_FAILOVER", att_diff_deg)
assert failover_latency_ms <= 100, "DO-178C DAL-C FAIL"
```
**Çıktı:** `dual_imu.json` | **Kriter:** Failover ≤ 100 ms | **Std:** DO-178C Level C

---
### `WBS 7.11` ESC/Motor Sağlık Monitöring [NEW-v4]
**Script:** `motor_health.py`
```python
# DSHOT telemetri: RPM, I, T_esc
for i, motor in enumerate(motors):
    rpm_err_pct = abs(motor['RPM_actual'] - motor['RPM_cmd']) / motor['RPM_cmd'] * 100
    if rpm_err_pct > 5:
        health_flags[i] = "DEGRADED"
    if motor['T_esc_C'] > 80:
        power_derate[i] = 0.85
```
**Çıktı:** `motor_health.json` | **Kriter:** RPM anomali < 500 ms tespiti

---
### `WBS 9.6` Compass-Motor Kompanzasyon [NEW-v4]
**Script:** `compass_mot.py`
```python
# Her motor kombinasyonunda mag ölçümü → kompanzasyon matrisi
import numpy as np
# B_measured[i] = B_earth + Σ(B_motor_j(I_j))
# Least squares: M_comp = pinv(I_matrix) @ (B_measured - B_earth)
residual_mGauss = np.linalg.norm(B_corrected - B_earth) * 1e6
assert residual_mGauss < 3, "KK-COMPASS FAIL"
```
**Çıktı:** `compass_mot.json` | **Kriter:** Residual ≤ 3 mGauss

---
### `WBS 10.7` Log Analiz Pipeline [NEW-v4]
**Script:** `log_pipeline.py`
```python
from pyulog import ULog
import numpy as np, pandas as pd

log = ULog("flight.ulg")
df_att = pd.DataFrame(log.get_dataset('vehicle_attitude').data)
roll_rms = df_att['roll'].std()
anomaly_score = min(roll_rms / 1.0, 1.0)  # normalize 0-1
assert anomaly_score < 0.3, f"Log anomali: score={anomaly_score:.2f}"
```
**Çıktı:** `log_analysis.json` | **Kriter:** anomaly_score < 0.3

---
### `WBS 11.7` DO-178C Yazılım Doğrulama [NEW-v4]
**Script:** `sw_validation.py`
```bash
# Kod kapsama (gcovr)
gcovr --root . --html --output coverage.html
# Kapsama: statement ≥80%, MC/DC ≥70%

# MISRA-C statik analiz (cppcheck)
cppcheck --enable=all --suppress=missingInclude src/
# MISRA critical = 0

# DAL seviyesi belirleme
SAIL_to_DAL = {"SAIL-I": "DAL-D", "SAIL-II": "DAL-D",
               "SAIL-III": "DAL-C", "SAIL-IV": "DAL-B"}
```
**Çıktı:** `sw_validation.json` | **Kriter:** DAL uyumlu; stmt ≥80%; MISRA critical=0

---
### `WBS 12.4` Operatör Eğitim & TBO [NEW-v4]
**Script:** `operator_docs.py`
```python
# TBO hesabı (motor)
# Motor ömrü yaklaşımı: life_h = C1 / (RPM_avg/RPM_rated)^C2 × (T_avg/T_rated)^C3
TBO_motor_h = 200 * (1 - RPM_avg/RPM_max * 0.3) * (1 - T_motor_avg/T_max * 0.2)
# Batarya: SoH düşüş modeli
battery_cycle_max = int(1000 * (1 - 0.002 * avg_C_rate))
```
**Çıktı:** `operator_manual.md` + `maintenance_schedule.json`

---
### `WBS 12.5` Taşıma & Lojistik [NEW-v4]
**Script:** `logistics.py`
```python
# IATA DGR sınıflandırması
E_Wh = battery['E_Wh']
if E_Wh > 300:    IATA_class = "Class 9 - PI 968/969"
elif E_Wh > 100:  IATA_class = "Class 9 - PI 966/967 (cihaz içi)"
else:             IATA_class = "Exempt (PI 965/966)"
UN_number = "UN 3480" if not installed else "UN 3481"
```
**Çıktı:** `logistics.json` | **Kriter:** IATA sınıflandırması doğru

---
### `WBS 13.5` Performans Zarfı [NEW-v4]
**Script:** `perf_envelope.py`
```python
import numpy as np
rho_SL = 1.225  # kg/m³
altitudes = [0, 1000, 2000, 3000]  # m MSL
delta_temps = [-25, 0, 25, 35]     # ISA offset °C

TW_matrix = np.zeros((4, 4))
for i, alt in enumerate(altitudes):
    T_ISA = 288.15 - 0.0065*alt
    for j, dT in enumerate(delta_temps):
        rho = rho_SL * ((T_ISA + dT) / T_ISA)**4.256
        derate = rho / rho_SL
        TW_matrix[i,j] = base_TW * derate
# KK: TW_matrix.min() ≥ 1.5
assert TW_matrix.min() >= 1.5, f"KK-PERF-ENV FAIL: min T/W={TW_matrix.min():.2f}"
```
**Çıktı:** `perf_envelope.json` | **Kriter:** T/W ≥ 1.5 @ en kötü durum

---
### `WBS 14.6` Bow-Tie & SwFMEA [NEW-v4]
```python
# Bow-Tie tehlike bariyerleri
threats = {
    "Kontrolsüz_uçuş": {
        "sol_bariyerler": ["dual_IMU", "motor_health_mon", "geofence"],
        "sag_bariyerler": ["RTL", "LAND", "parachute"],
        "SORA_OSO": ["OSO-14", "OSO-15", "OSO-17", "OSO-18"]
    }
}
# SwFMEA: yazılım arıza modu × etki × SIL
SW_FMEA = [
    {"mode": "EKF_diverge", "severity": 4, "prob": 2, "detect": 3, "RPN": 24},
    {"mode": "motor_mix_err","severity": 5, "prob": 1, "detect": 2, "RPN": 10},
]
```
**Çıktı:** `bowtie.json` | **Kriter:** Tüm SORA OSO-14..18 uyum durumu

---
## 🏭 WBS 15 — CI/CD & YAZILIM KALİTE GÜVENCESİ [YENİ FAZ]

### `WBS 15.1` CI/CD Pipeline
```yaml
# .github/workflows/ci.yml  (LLM tarafından üretilir)
name: MultiCopter CI
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint
        run: ruff check . && mypy src/
      - name: Unit Tests
        run: pytest tests/ --junitxml=results.xml
      - name: Coverage
        run: gcovr --fail-under-line 80
      - name: SITL Regression
        run: python sitl_regression.py
      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          path: results.xml
```
**Kriter:** Tüm aşamalar PASS; coverage ≥ 80%; her commit tetikleniyor

### `WBS 15.2` SITL Regresyon
```python
# sitl_regression.py — 4 otomatik test
TESTS = [
    {"name": "hover_30s",   "kk": "KK-11", "limit": 1.0,  "param": "roll_rms_deg"},
    {"name": "mission_10wp","kk": "KK-11", "limit": 1.0,  "param": "cross_track_m"},
    {"name": "gust_5ms",    "kk": "gust",  "limit": 2.0,  "param": "pos_dev_m"},
    {"name": "OEI_land",    "kk": "OEI",   "limit": True, "param": "landing_OK"},
]
```

### `WBS 15.3` MISRA-C Statik Analiz
```bash
cppcheck --enable=all --std=c99 --suppress=missingInclude src/
# MISRA critical = 0 (ZORUNLU)
# Advisory ≤ 10 (hedef)
# McCabe complexity ≤ 10/fonksiyon
```

---
## 📋 STD DÜZELTMELERİ v4

| WBS | Eski | Yeni |
|-----|------|------|
| WBS 4.1 | IEC 62133 (kalıntı) | **IEC 62619** |
| WBS 4.4 | IEC 62133 (kalıntı) | **IEC 62619** |
| WBS 8.2 | RTCA DO-365 | **EUROCAE ED-269** |

---
## ✅ 13. KALİTE KAPISI (v4 ekleme)

**KK-13: Yaw Torque Dengesi**
```python
Q_imbalance = abs(sum(sign_i * Q_i for sign_i, Q_i in zip(rotation_dirs, Q_per_rotor)))
assert Q_imbalance <= 0.01, f"KK-13 FAIL: Q_imb={Q_imbalance:.4f} N·m"
```
Başarısız → WBS 2.3: rotation_dirs[] yeniden ata

---
*MultiCopter WBS v4.0 Delta — Nisan 2026 | v3 + 13 yeni görev + 3 STD fix*


---

## 📚 V3 TAM TALİMAT (REFERANS)

# 🚁 MULTİCOPTER TASARIMI — LLM UYGULAMA TALİMATI v3.0

> **Bu dosya LLM ajanına verilecek tam uygulama talimatıdır.**
> **v3.0:** 32 hata düzeltildi · 12 yeni görev · Standartlar güncellendi
> Her WBS fazı sırayla uygulanır. `validation_passed: True` olmadan sonraki faza geçilmez.

---
## 📌 ZORUNLU KURALLAR

1. **Adım atlama yasak.** Her WBS çıktısını JSON üret, Pydantic doğrula, sonra devam et.
2. **KK başarısız → MDAO geri dönüş.** Tablo: hangi KK → hangi WBS'e dön (v3 tutarlı adresler).
3. **Tüm birimler SI.** [kg, m, N, W, °, Hz, N·m] — istisna yoktur.
4. **Belirsiz girdi → sor.** Sayısal değer yoksa tahmin etme, kullanıcıya sor.
5. **Max iterasyon = 5.** Aşılırsa `escalation_report.json` üret, insan mühendise ilet.
6. **[TECH] düzeltmeler zorunlu.** Eski hatalı formüller (sabit phi, boş KV, vb.) kullanılmaz.
7. **Cross-validation (WBS 14.4).** T_total=n×T_per_rotor ±1%; E_Wh/V×1000=C_mAh ±2%.

---
## 🛠️ KRİTİK TEKNİK DÜZELTMELER [v3]

### BEMT — Doğru Glauert İterasyonu
```python
# [TECH-FIX] Sabit phi=0.05 HATASI — Glauert iteratif çözüm kullanılmalı
for ri, r in enumerate(r_annuli):
    phi = np.arctan2(v_induced[ri], Omega * r)  # başlangıç tahmini
    for _ in range(100):
        alpha = theta_twist - phi
        CL = CL_alpha * alpha
        CD = CD0 + CL**2 / (pi * AR_blade)
        f_tip = (2/pi) * arccos(exp(-n_b*(1-r/R)/(2*sin(phi))))  # Prandtl
        v_i_new = (Omega*r * n_b*chord*(CL*cos(phi)-CD*sin(phi))) / (8*pi*r*f_tip)
        phi_new = arctan2(v_i_new, Omega*r)
        if abs(phi_new - phi) < 1e-6: break
        phi = phi_new
```

### Motor KV — Yüklü Model
```python
# [TECH-FIX] Boş yük KV (hatalı): KV_ideal = RPM / V_batt
# Yüklü model (doğru):
R_int = motor['R_int_Ohm']  # iç direnç
I_hover = P_per_rotor / (V_batt * eta_motor)
V_loaded = V_batt - I_hover * R_int
KV_required = RPM_hover / V_loaded  # gerçek KV gereksinimi
```

### EKF — Q ve R Matrisleri (Zorunlu)
```python
# [TECH-FIX] Q ve R tanımsız bırakılmaz
sigma_acc  = 0.01   # m/s² IMU ivme gürültüsü
sigma_gyro = 0.001  # rad/s jiroskop gürültüsü
sigma_bias = 1e-5   # bias drift
sigma_gps_pos = 0.5 # m GPS pozisyon
sigma_gps_vel = 0.1 # m/s GPS hız
sigma_baro = 0.5    # m barometrik irtifa
Q = np.diag([sigma_acc**2]*3 + [sigma_gyro**2]*3 + [sigma_bias**2]*3)
R = np.diag([sigma_gps_pos**2]*3 + [sigma_gps_vel**2]*3 + [sigma_baro**2])
```

### Cheeseman-Bennett Ground Effect (Zorunlu)
```python
# [TECH-FIX] Formül koda eklendi
def IGE_ratio(z_m, D_rotor_m):
    z_over_D = z_m / D_rotor_m
    if z_over_D >= 1.0:
        return 1.0  # OGE (ground effect yok)
    return 1.0 / (1.0 - (D_rotor_m / (4 * z_m))**2)
T_IGE = T_OGE * IGE_ratio(z_hover, D_rotor)  # Cheeseman & Bennett 1955
```

### B_matrix — Singularity Kontrolü (Zorunlu)
```python
# [TECH-FIX] Condition number check eklendi
import numpy as np
cond = np.linalg.cond(B_matrix)
rank = np.linalg.matrix_rank(B_matrix)
assert rank == 4, f'B_matrix rank={rank} < 4 — konfigürasyon yetersiz'
assert cond < 50, f'B_matrix ill-conditioned: cond={cond:.1f}'
```

---
## 🗂️ FAZ ÖZET TABLOSU (v3)

| # | Faz | Çıktı JSON | Araçlar | Değişiklik |
|---|-----|-----------|---------|------------|
| 1 | Görev & Gereksinim | `mission_profile+requirements+regulation` | LLM NLP+Python | m_misc eklendi |
| 2 | Konfig & Geometri | `phase_2_geometry+yaw_balance+cg` | OpenVSP+CadQuery | yaw_balance [NEW]; lg_FEA [FIX] |
| 3 | İtki (BEMT+Motor) | `phase_3_thrust+bemt+balance` | BEMT+UIUC+QBlade | Glauert iter+yüklü KV+burst ESC [TECH] |
| 4 | Güç & Enerji | `phase_4_energy+bms+charger+emi` | Python+Pydantic | charger [NEW]; IEC 62619 [STD] |
| 5 | Aerodinamik | `airfoil+interaction+noise` | NeuralFoil+FW-H | FW-H gürültü [TECH]; ISO 3744 [STD] |
| 6 | Yapısal & Termal | `fea+arm_sizing+mount_stiffness+thermal` | CalculiX+scipy | mount_stiffness [NEW]; Campbell Hz fix [TECH] |
| 7 | GNC & Kontrol | `dynamics+controller+nav+mixing` | python-control+filterpy | anti-windup+altitude_ctrl [NEW]; Q/R [TECH] |
| 8 | Haberleşme | `rc_link+c2_link+comm_security+datalog` | Python+MAVLink | comm_security [NEW]; DO-316A [STD] |
| 9 | Sensör & Payload | `sensor_calib+payload+gimbal+preflight` | Python+ROS2 | sensor_calib [NEW] |
| 10 | SITL & HITL | `sitl_hover+sitl_mission+monte_carlo` | Gazebo+PX4 | Monte Carlo [NEW] |
| 11 | Fiziksel Test | `bench+balance+env_test+flight+safety` | Python DAQ | env_test DO-160G [NEW] |
| 12 | Üretim | `bom+assembly+qa` | Python+LLM | ESD+FOD prosedür |
| 13 | MDAO Optimizasyon | `kk_summary+sensitivity+pareto` | OpenMDAO+pymoo | sensitivity [NEW]; FAST indeks |
| 14 | LLM Rapor | `final_design+report+sha256` | LLM+Pydantic | cross-validation [NEW]; SHA256 |

---
## WBS 1.0 — AŞAMA 1 Görev & Gereksinim Analizi

### `WBS 1.1` Görev Profili & Uygulama Senaryosu

**Yazılım:** LLM (Python)  **|**  **Kaynak:** Kullanıcı

**Standart:** ASTM F3002-14a | ISO 21384-3 | EUROCAE ED-269

**LLM Girdisi:** `Doğal dil görev tanımı (kargo/tarım/gözetleme/BVLOS/yarış/insansız hava taksi)`

**Script:**
```python
mission_parser.py  # NLP → structured JSON; uygulama tipi → parametre seti
```

**Beklenen Çıktı:** `mission_profile.json: app_type, payload_kg, range_km, endurance_min, altitude_m, wind_bft, ops_env, flight_type`

**✅ Kabul Kriteri:** Tüm görev parametreleri sayısal ve eksiksiz; belirsiz alan → LLM kullanıcıya sorar

### `WBS 1.2` Performans Gereksinim Matrisi (PRD)

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 1.1

**Standart:** Raymer §17 | NDARC NASA/TM-2015-218751 | Staufenbiel

**LLM Girdisi:** `mission_profile.json + operasyonel kısıtlar`

**Script:**
```python
prd_sizing.py  # T/W, endurance, V_max, payload_fraction; Staufenbiel iteratif
```

**Beklenen Çıktı:** `requirements.json: MTOW_kg, T_W_req≥2.0, endurance_min, V_max_ms, V_cruise_ms, redundancy`

**✅ Kabul Kriteri:** T/W_req ≥ 2.0; payload_fraction ≥ 0.15; tüm değerler kaynaklandırılmış

### `WBS 1.3` Mevzuat Sınıfı & SORA Risk Değerlendirmesi

**Yazılım:** LLM (NLP+Python)  **|**  **Kaynak:** WBS 1.1

**Standart:** EASA (EU) 2019/945 | JARUS SORA v2.5 | FAA Part 107 | ASTM F3411-22a

**LLM Girdisi:** `MTOW_kg + ops_env + flight_type (VLOS/BVLOS)`

**Script:**
```python
sora_assessment.py  # GRC, ARC, SAIL seviyesi; OSO ataması; operational volume
```

**Beklenen Çıktı:** `regulation.json: EASA_cat, SAIL_level, GRC, ARC, OSO_list[], DO160_class, RID_required`

**✅ Kabul Kriteri:** SAIL seviyesi hesaplanmış; tüm OSO'lar atanmış; RID gereksinimi belirlendi

### `WBS 1.4` Başlangıç Kütle Bütçesi (Weight Statement) 🔧[TECH-FIX]

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 1.2

**Standart:** Staufenbiel | NDARC | Raymer §15 — [TECH: m_misc eklendi]

**LLM Girdisi:** `requirements.json: MTOW, payload, endurance`

**Script:**
```python
mass_budget.py  # TECH-FIX: kablo+bağlantı+sealant kütlesi dahil edildi
# m_misc = 0.03×MTOW (kablo/bağlantı/yapıştırıcı/güvenlik öğeleri)
# Raymer grup ağırlık yöntemi + misc_fraction
```

**Beklenen Çıktı:** `mass_budget.json: m_frame, m_motors, m_esc, m_battery, m_avionics, m_payload, m_cables, m_misc, m_total`

**✅ Kabul Kriteri:** Σm_bileşen ≤ MTOW_kg; m_misc ≥ 0.02×MTOW dahil edilmiş; kapanış hatası < 1%

### `WBS 1.5` Trade-Off Analizi — Konfigürasyon Alternatifleri

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 1.2+1.4

**Standart:** INCOSE SE Handbook v4 | Pugh Matrix | AHP yöntemi

**LLM Girdisi:** `requirements.json + tradeoff_criteria.json`

**Script:**
```python
tradeoff.py  # Pugh matrix: Quad/Hex/Octo × X/H/+ × Coax; ağırlıklı puan
```

**Beklenen Çıktı:** `tradeoff.json: alternatives[], scores[], selected_config, justification, sensitivity_notes`

**✅ Kabul Kriteri:** Seçim puanlama matrisiyle gerekçelendirilmiş; en az 3 alternatif karşılaştırılmış

---
## WBS 2.0 — AŞAMA 2 Konfigürasyon & 3D Geometri

### `WBS 2.1` Rotor Sayısı & Dizilim Seçimi

**Yazılım:** LLM (Python karar ağacı)  **|**  **Kaynak:** WBS 1.5

**Standart:** NDARC | Prouty Rotorcraft Aero | [NEW: rotation_dirs yaw torque dengesi]

**LLM Girdisi:** `tradeoff.json + requirements.json`

**Script:**
```python
config_select.py  # payload>5kg→hex/octo; BVLOS→n≥6; coaxial: yüksek disk loading
```

**Beklenen Çıktı:** `config.json: n_rotors, layout(X/H/+/Y6), coaxial_flag, arm_fold_flag, redundancy, rotation_dirs[]`

**✅ Kabul Kriteri:** Konfigürasyon gerekçeli; rotation_dirs[] CW/CCW dönüşleri atanmış (yaw dengesi)

### `WBS 2.2` Rotor Çapı & Wheelbase Hesabı

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 2.1+1.2

**Standart:** Leishman §2 | AHS Forum 2019

**LLM Girdisi:** `config.json + MTOW_kg + DL_target`

**Script:**
```python
geometry_sizing.py  # D=2√(T_per_rot/(ρπ×DL)); WB=D×s_D×f_layout
```

**Beklenen Çıktı:** `geometry.json: D_rotor_m, wheelbase_m, arm_length_m, s_D_ratio, hub_diam_m, tip_clearance_m`

**✅ Kabul Kriteri:** s/D ≥ 1.1; tip_clearance_m ≥ 0.05; D_rotor ile s_D tutarlı

### `WBS 2.3` Yaw Torque Dengesi Analizi 🆕[NEW]

**Yazılım:** LLM (Python)  [NEW]  **|**  **Kaynak:** WBS 2.1+3.2

**Standart:** Prouty §4 | Mahony 2012 | [NEW: multirotor yaw denge kritik kontrolü]

**LLM Girdisi:** `config.json: rotation_dirs[] + bemt.json: Q_per_rotor_Nm`

**Script:**
```python
yaw_balance.py  # ΣQ_CW = ΣQ_CCW; yaw moment imbalance < eşik
# Q_yaw_imbalance = |Σ(sign_i × Q_i)| ≤ 0.01 N·m @ hover
```

**Beklenen Çıktı:** `yaw_balance.json: Q_CW_Nm, Q_CCW_Nm, Q_imbalance_Nm, yaw_balanced_flag`

**✅ Kabul Kriteri:** Yaw torque dengesizliği ≤ 0.01 N·m @ hover; rotation_dirs[] güncellenmiş

### `WBS 2.4` OpenVSP 3D Geometri Modeli

**Yazılım:** OpenVSP 3.x Python API  **|**  **Kaynak:** WBS 2.2

**Standart:** OpenVSP NASA | MIL-HDBK-1797B

**LLM Girdisi:** `geometry.json + config.json`

**Script:**
```python
vsp_build.py  # Hub:POD + Kollar:FUSELAGE×n + Motor mount POD'ları
# vsp.ClearVSPModel(); hub; arms; motor_pods; vsp.Update()
```

**Beklenen Çıktı:** `mc.vsp3 + mc.stl + mc.step  (Katman-1 OML)`

**✅ Kabul Kriteri:** vsp.Update() hatasız; STL watertight; bileşen isimleri standart (Hub/Arm_0..n/MotorMount_i)

### `WBS 2.5` Kol & Motor Mount Mekanik Tasarımı (CadQuery)

**Yazılım:** CadQuery + LLM  **|**  **Kaynak:** WBS 2.2+6.1

**Standart:** MIL-HDBK-5J | ASTM D3039 | CadQuery Docs

**LLM Girdisi:** `geometry.json + arm_sizing.json (WBS 6.1'den)`

**Script:**
```python
arm_cad.py  # CFRP boru + motor mount flanş + katlama menteşesi
# CQ: tube(D_out, t_wall, L_arm) + mount_flange(pattern_mm)
```

**Beklenen Çıktı:** `arm_design.json: D_out_mm, t_wall_mm, mount_bolt_pattern_mm, fold_hinge_type, cad_file`

**✅ Kabul Kriteri:** Motor titreşim frekansı ≠ kol modal frekansı; cad_file STEP formatında

### `WBS 2.6` İniş Takımı Geometrisi & Darbe Yük Analizi

**Yazılım:** LLM (Python)  [FIXED]  **|**  **Kaynak:** WBS 2.4

**Standart:** FAR/CS 23.473 | EASA SC-VTOL §2520 | MIL-HDBK-5J

**LLM Girdisi:** `geometry.json + mass_budget.json`

**Script:**
```python
landing_gear.py  # 1.5g dikey darbe yükü; boru burkulma; enerji absorpsiyonu
# F_impact = MTOW × g × 1.5; σ_leg = F_impact × L / I_leg × c_leg
```

**Beklenen Çıktı:** `landing_gear.json: height_m, track_m, tip_clearance_m, F_impact_N, MS_leg, material`

**✅ Kabul Kriteri:** MS_leg ≥ 1.5 @ 1.5g darbe; tip_clearance ≥ 0.05 m; [FIXED: FEA dahil]

### `WBS 2.7` CG Analizi — 3 Konfigürasyon + CG Zarfı

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 2.4+1.4

**Standart:** EASA SC-VTOL §2510 | Raymer §6

**LLM Girdisi:** `mc.vsp3 + mass_budget.json`

**Script:**
```python
cg_envelope.py  # Dolu/Yakıtsız/Yüksüz × 3 eksen; zarf hesabı
```

**Beklenen Çıktı:** `cg.json: cg_x_mm, cg_y_mm, cg_z_mm, cg_deviation_mm, cg_envelope_mm, configs{}`

**✅ Kabul Kriteri:** CG sapması ≤ 5 mm (tüm konfigürasyonlar); CG zarfı hesaplanmış

### `WBS 2.8` OpenVSP Pydantic Çıktı Standardizasyonu

**Yazılım:** LLM (Python/Pydantic)  **|**  **Kaynak:** WBS 2.4-2.7

**Standart:** Pydantic v2 | Dahili şema

**LLM Girdisi:** `mc.vsp3 mass_props + geometry.json`

**Script:**
```python
parse_vsp_mc.py  # vsp mass_props → Pydantic GeometryResult
```

**Beklenen Çıktı:** `phase_2_geometry.json  (validation_passed: true)`

**✅ Kabul Kriteri:** validation_passed: True; yaw_balanced: True; tüm zorunlu alanlar dolu

---
## WBS 3.0 — AŞAMA 3 İtki Sistemi — BEMT & Motor

### `WBS 3.1` Disk Yükleme & Hover Momentum Analizi

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 2.2

**Standart:** Leishman §2 | NDARC NASA/TM-2015-218751

**LLM Girdisi:** `MTOW_kg, n_rotors, D_rotor_m, altitude_m`

**Script:**
```python
hover_momentum.py  # DL=T/A; P_ideal=T√(T/2ρA); PL=T/P_ideal; irtifa düzeltmesi dahil
# rho = rho_SSL × (1-0.0000225577×alt)^4.2561
```

**Beklenen Çıktı:** `momentum.json: DL_Nm2, PL_NW, P_ideal_W, v_induced_ms, FM_target, rho_alt`

**✅ Kabul Kriteri:** DL ≤ 300 N/m²; PL ≥ 8 N/W; irtifa düzeltmeli rho kullanılmış

### `WBS 3.2` BEMT Pervane Analizi (Tam Glauert İterasyonu) 🔧[TECH-FIX]

**Yazılım:** Python BEMT / QBlade  [TECH-FIX]  **|**  **Kaynak:** WBS 3.1

**Standart:** Leishman §3 | JBLADE | UIUC Prop DB — [TECH: Glauert iterasyon düzeltildi]

**LLM Girdisi:** `D_rotor, n_blades, chord_dist[], twist_dist[], airfoil_CL_CD_tables`

**Script:**
```python
bemt.py  # TECH-FIX: Glauert iteratif çözüm (sabit phi=0.05 HATASI DÜZELTİLDİ)
# Her annulusta: phi_new=atan(v_i/(Ω×r)) iterate until |phi_new-phi|<1e-6
# dT=0.5ρΩ²r²n_b×c×(CL×cos(phi)-CD×sin(phi))×dr×f_Prandtl
# f_Prandtl = Prandtl tip loss correction
```

**Beklenen Çıktı:** `bemt.json: CT, CQ, CP, FM, eta_prop, RPM_hover, T_N, Q_Nm, P_W, f_tip_loss`

**✅ Kabul Kriteri:** FM ≥ 0.60; Prandtl uç kaybı dahil; iterasyon konverje < 1e-6

### `WBS 3.3` Ground Effect Analizi (Cheeseman-Bennett) 🔧[TECH-FIX]

**Yazılım:** LLM (Python)  [TECH-FIX]  **|**  **Kaynak:** WBS 3.2

**Standart:** Cheeseman & Bennett 1955 | Leishman §7 — [TECH: formül koda eklendi]

**LLM Girdisi:** `D_rotor_m, T_OGE_N, z_hover_m`

**Script:**
```python
ground_effect.py  # TECH-FIX: Cheeseman-Bennett formülü koda eklendi
# T_IGE/T_OGE = 1 / (1 - (D/(4z))^2)  — Cheeseman & Bennett 1955
# Geçerlilik: z/D < 1.0; uyarı: z/D > 1.0 → OGE
```

**Beklenen Çıktı:** `ground_effect.json: T_IGE_N, T_OGE_N, IGE_ratio, z_thresh_m, P_IGE_W`

**✅ Kabul Kriteri:** IGE/OGE oranı hesaplanmış; kalkış güç bütçesi IGE ile güncellenmiş

### `WBS 3.4` Coaxial Rotor Analizi (Düzeltilmiş FM Hedefi) 🔧[TECH-FIX]

**Yazılım:** Python BEMT  [TECH-FIX]  **|**  **Kaynak:** WBS 3.2

**Standart:** Leishman §8 | Prouty §4 — [TECH: FM_coax hedefi 0.55→0.60 düzeltildi]

**LLM Girdisi:** `config.json: coaxial_flag=True; üst/alt rotor geometrisi`

**Script:**
```python
coax_bemt.py  # Alt rotor inflow: v_i_lower = v_i_upper × k_int (k_int≈1.25)
# TECH-FIX: Coaxial FM hedefi 0.60-0.65 (0.55 HATASI DÜZELTİLDİ)
# T_coax = T_upper + T_lower; FM_coax = T_coax√(T_coax/2ρA) / P_coax
```

**Beklenen Çıktı:** `coax.json: T_upper_N, T_lower_N, FM_coax, k_interference, P_coax_W`

**✅ Kabul Kriteri:** Coaxial FM ≥ 0.60 (Leishman Fig 8.17 referans); k_int ≈ 1.25

### `WBS 3.5` Pervane Seçimi & Motor-Pervane Eşleştirme Opt. 🔧[TECH-FIX]

**Yazılım:** LLM (Python)+UIUC DB  [TECH-FIX]  **|**  **Kaynak:** WBS 3.2+4.1

**Standart:** UIUC Prop DB | APC | T-Motor — [TECH: yüklü KV formülü düzeltildi]

**LLM Girdisi:** `bemt.json + D_rotor + RPM_hover + V_battery + I_hover_A`

**Script:**
```python
prop_match.py  # TECH-FIX: Yüklü KV modeli
# KV_ideal = RPM_hover / V_batt  (boş yük)
# KV_loaded = RPM_hover / (V_batt - I_hover×R_int)  (yüklü, daha doğru)
# UIUC DB: CT/CP eşleştirme ± 5% tolerans
```

**Beklenen Çıktı:** `propeller.json: model, D_m, pitch_m, n_blades, CT, CP, RPM_nom, KV_required_loaded`

**✅ Kabul Kriteri:** KV_loaded ile motor seçimi; statik thrust ≥ T_hover × 1.2

### `WBS 3.6` BLDC Motor Seçimi & Tork-Güç Doğrulama 🔧[TECH-FIX]

**Yazılım:** LLM (Python+Spec)  **|**  **Kaynak:** WBS 3.5+4.1

**Standart:** T-Motor/Dualsky datasheets | [TECH: R_int yüklü model]

**LLM Girdisi:** `propeller.json + V_battery + eta_motor_min + R_int_motor`

**Script:**
```python
motor_select.py  # Q_prop=CP×ρ×n²×D⁵/(2π); P_shaft=Q×Ω
# TECH-FIX: R_int dahil yüklü gerilim: V_loaded=V_batt-I×R_int
```

**Beklenen Çıktı:** `motor.json: model, KV, P_max_W, Q_max_Nm, R_int_Ohm, eta_motor, weight_g, Tmax_C`

**✅ Kabul Kriteri:** eta_motor ≥ 0.85; R_int < 0.1 Ω; termal marj ≥ 20% altında T_max

### `WBS 3.7` ESC Seçimi & Akım Doğrulama 🔧[TECH-FIX]

**Yazılım:** LLM (Spec Parser)  [TECH-FIX]  **|**  **Kaynak:** WBS 3.6

**Standart:** PX4 Hardware Std. | BLHeli_32 | [TECH: burst akım kontrolü eklendi]

**LLM Girdisi:** `motor.json: I_max_A, P_max_W + kalkış profili`

**Script:**
```python
esc_select.py  # TECH-FIX: Hem sürekli hem burst akım kontrolü
# I_kalkış = T_max / (KV × V_batt × eta_mot) × 1.5  (burst ~%150)
# I_cont ≥ I_hover × 1.25; I_burst ≥ I_kalkış × 1.10
```

**Beklenen Çıktı:** `esc.json: model, I_cont_A, I_burst_A, I_burst_duration_s, protocol, BEC, weight_g`

**✅ Kabul Kriteri:** I_cont ≥ 1.25×I_hover; I_burst ≥ 1.10×I_kalkış; protokol DSHOT600

### `WBS 3.8` Pervane Statik & Dinamik Balans Prosedürü

**Yazılım:** LLM (Prosedür üretimi)  **|**  **Kaynak:** WBS 3.5

**Standart:** ISO 1940-1 G1 | PX4 Vibration Guide

**LLM Girdisi:** `propeller.json + RPM_hover + rotor_mass_g`

**Script:**
```python
balance_proc.py  # ISO 1940 G1 sınıfı; balanssızlık limiti U_perm = e × m
# e_perm (G1) = 9549 × G1_grade / RPM_max mm/s → μm spesifik dengesizlik
# Dinamik: 2 düzlemde balans; IMU FFT @ RPM_hover doğrulama
```

**Beklenen Çıktı:** `balance_procedure.md + balance_target.json: G_class, e_perm_mm, U_perm_g_mm, planes`

**✅ Kabul Kriteri:** 1P titreşim ≤ 0.05 g; U_perm ISO 1940 G1 karşılanmış

### `WBS 3.9` İtki Zinciri Sistem Doğrulama & T/W

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 3.6-3.7+2.3

**Standart:** NDARC | MIL-HDBK-516C §15

**LLM Girdisi:** `motor+esc+propeller+mass_budget+yaw_balance`

**Script:**
```python
thrust_verify.py  # T_total=n×T_rot; TW=T/(MTOW×g); yaw imbalance dahil
```

**Beklenen Çıktı:** `thrust_chain.json: T_total_N, TW_ratio, P_total_hover_W, sys_efficiency, yaw_balanced`

**✅ Kabul Kriteri:** T/W ≥ 2.0; sys_efficiency ≥ 0.70; yaw_balanced: True (KK-1)

---
## WBS 4.0 — AŞAMA 4 Güç & Enerji Sistemi

### `WBS 4.1` Batarya Teknoloji Seçimi & Trade-Off 📋[STD-FIX]

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 1.2+3.9

**Standart:** ASTM F3005-14a | IEC 62619 | UN 38.3 | DO-311A — [STD: IEC 62133→62619]

**LLM Girdisi:** `endurance_min, P_hover_W, MTOW_kg, ops_temp_C`

**Script:**
```python
battery_chem.py  # LiPo/Li-Ion/LiFePO4 Wh/kg×C-rate×sıcaklık trade
# LiPo: 180-220 Wh/kg, 25C cont; Li-Ion: 200-260 Wh/kg, 3-5C cont
```

**Beklenen Çıktı:** `battery_chem.json: chemistry, Wh_kg, C_rate_cont, C_rate_burst, T_min_C, T_max_C`

**✅ Kabul Kriteri:** Wh/kg ≥ 180; C_rate_cont ≥ hover_C_rate; sıcaklık aralığı ops ile uyumlu

### `WBS 4.2` Batarya Kapasite & S/P Konfigürasyonu

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 4.1+3.9

**Standart:** ASTM F3005 | FAA AC 20-184

**LLM Girdisi:** `battery_chem.json + P_hover_W + endurance_min`

**Script:**
```python
battery_size.py  # E_req=P_hover×t/η_batt; C_mAh=E_Wh/V_nom×1000
# Peukert kaybı: C_eff = C_nom × (I_nom/I_hover)^(n_Peukert-1)
```

**Beklenen Çıktı:** `battery.json: S, P, V_nom, C_mAh, E_Wh, C_nom_mAh, weight_kg, discharge_C`

**✅ Kabul Kriteri:** t_hover ≥ endurance_min × 1.2; rezerv ≥ %20; Peukert dahil (KK-3)

### `WBS 4.3` Şarj Sistemi & Balans Şarj Prosedürü 🆕[NEW]

**Yazılım:** LLM (Python)  [NEW]  **|**  **Kaynak:** WBS 4.2

**Standart:** IEC 62619 | UN 38.3 | LiPo Güvenlik Rehberi — [NEW]

**LLM Girdisi:** `battery.json: S, C_mAh, chemistry`

**Script:**
```python
charger_design.py  # CC-CV şarj profili; balans şarj toleransı ΔV < 5mV
# Hızlı şarj: C_rate_charge ≤ 2C (LiPo güvenlik sınırı)
# Depolama voltajı: 3.8V/hücre
```

**Beklenen Çıktı:** `charger.json: charge_rate_C, balance_dV_mV, storage_V_cell, charge_time_min, charger_model`

**✅ Kabul Kriteri:** ΔV_balance ≤ 5 mV; şarj hızı ≤ 2C; depolama voltajı 3.8 V/hücre

### `WBS 4.4` BMS (Batarya Yönetim Sistemi) Tasarımı 📋[STD-FIX]

**Yazılım:** LLM (Spec Parser)  **|**  **Kaynak:** WBS 4.2

**Standart:** IEC 62619 | UN 38.3 | RTCA DO-311A — [STD: IEC 62133→62619 düzeltildi]

**LLM Girdisi:** `battery.json: S, I_max_A`

**Script:**
```python
bms_design.py  # OVP/UVP/OCP/OTP/SCP; pasif/aktif balans; comm arayüzü
# OVP=4.20V±0.05, UVP=3.00V±0.05, OCP=I_max×1.1
```

**Beklenen Çıktı:** `bms.json: OVP_V, UVP_V, OCP_A, OTP_C, SCP_flag, balance_type, comm, weight_g`

**✅ Kabul Kriteri:** Tüm 5 koruma fonksiyonu aktif; balance_type: active veya passive

### `WBS 4.5` Güç Dağıtım Kartı (PDB) & Kablolama

**Yazılım:** LLM (Python+Spec)  **|**  **Kaynak:** WBS 3.9+7.1

**Standart:** IEC 60364-7-712 | DO-160G §16

**LLM Girdisi:** `thrust_chain.json + avionics_power_W`

**Script:**
```python
pdb_size.py  # I_PDB=Σ(n×I_mot+avionics); AWG: I_max/A_mm2≤3A/mm2
# Güvenlik: I_PDB ≥ I_total×1.30; sigorta: I_fuse=I_PDB×1.15
```

**Beklenen Çıktı:** `pdb.json: I_rating_A, V_max, BEC_5V, BEC_12V, AWG, fuse_A, weight_g`

**✅ Kabul Kriteri:** I_PDB ≥ I_total×1.30; kablo AWG hesaplanmış; sigorta değeri belirlenmiş

### `WBS 4.6` EMI/EMC Analizi & Gürültü Azaltma 📋[STD-FIX]

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 3.6+4.5

**Standart:** DO-160G §21 | RTCA DO-316A | FCC Part 15 — [STD: DO-316→DO-316A]

**LLM Girdisi:** `motor.json: RPM_max + esc.json: switching_freq + GPS/IMU konumları`

**Script:**
```python
emi_analysis.py  # ESC switching harmonikleri (f_sw × 1..5)
# GPS L1=1575.42 MHz ayrıştırma; ferrit boncuk + kalkan tasarımı
```

**Beklenen Çıktı:** `emi.json: switching_harmonics_Hz[], GPS_SNR_dB, GPS_separation_mm, shielding_type`

**✅ Kabul Kriteri:** GPS SNR ≥ 35 dB; ESC→GPS bant ayrımı ≥ 100 MHz; kalkan belirlenmiş

### `WBS 4.7` Enerji Yönetimi & Uçuş Süresi Tahmini

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 4.2+3.9+5.3

**Standart:** NDARC §4 | Peukert modeli

**LLM Girdisi:** `battery.json + thrust_chain.json + fwd_flight.json`

**Script:**
```python
endurance.py  # P(v)=P_hover+P_parasitic(v²); Peukert kaybı
# t_max = E_usable / P_avg; reserve = E_total × 0.20
```

**Beklenen Çıktı:** `energy_budget.json: t_hover_min, t_cruise_min, range_km, reserve_pct, E_usable_Wh`

**✅ Kabul Kriteri:** t_hover ≥ endurance_min; rezerv ≥ %20; Peukert dahil

---
## WBS 5.0 — AŞAMA 5 Aerodinamik & Rotor Dinamiği

### `WBS 5.1` Düşük Re Airfoil Analizi (Pervane Profili)

**Yazılım:** NeuralFoil / XFoil  **|**  **Kaynak:** WBS 3.2

**Standart:** UIUC Airfoil DB | NeuralFoil | Abbott & von Doenhoff

**LLM Girdisi:** `airfoil.dat + Re_tip_range + Mach_tip`

**Script:**
```python
airfoil_analysis.py  # Re_tip=ρ×V_tip×c_tip/μ; NeuralFoil polar 5 Re noktası
# V_tip=Ω×R; Mach_tip=V_tip/a (kompresibilite kontrolü)
```

**Beklenen Çıktı:** `airfoil.json: CL_alpha, CD_min, CL_max, LD_max, Re_tip, stall_alpha_deg`

**✅ Kabul Kriteri:** CD_min ≤ 0.015; L/D_max ≥ 15; Mach_tip < 0.7 (kompresibilite sınırı)

### `WBS 5.2` Rotor-Rotor Aerodinamik Etkileşim

**Yazılım:** AeroSandbox / Python  **|**  **Kaynak:** WBS 2.2+3.2

**Standart:** Leishman §5 | Lerche 2015 | AHS Forum

**LLM Girdisi:** `geometry.json: s_D_ratio + RPM_hover + D_rotor`

**Script:**
```python
rotor_interact.py  # Momentum overlap: Δη = f(s/D); Lerche 2015 fit
# η_int = 1 - 0.15×exp(-3.5×(s/D - 1))
```

**Beklenen Çıktı:** `interaction.json: efficiency_loss_pct, effective_FM, downwash_ms, s_D_ratio`

**✅ Kabul Kriteri:** Etkileşim kaybı ≤ %8; s/D ≥ 1.1 (KK-8)

### `WBS 5.3` İleri Uçuş Trim & Güç Analizi

**Yazılım:** Python BEMT+AeroSandbox  **|**  **Kaynak:** WBS 3.9+5.1

**Standart:** Prouty §4 | Bramwell Helicopter Dynamics

**LLM Girdisi:** `thrust_chain.json + geometry.json + V_cruise_ms`

**Script:**
```python
fwd_flight.py  # θ=atan(D_par/W); P_fwd=T×V_sin(θ)+P_ind_fwd
# D_par: gövde+kol paralel sürüklemesi; P_ind_fwd = T²/(2ρA×V×cos(θ))
```

**Beklenen Çıktı:** `fwd_flight.json: tilt_deg, P_cruise_W, V_trim_ms, D_parasite_N, LD_eff`

**✅ Kabul Kriteri:** Tilt ≤ 30°; P_cruise ≤ P_hover × 0.85; D_parasite hesaplanmış

### `WBS 5.4` Rüzgar Gustu Tepki Analizi

**Yazılım:** LLM (Python+scipy)  **|**  **Kaynak:** WBS 7.1+7.3

**Standart:** MIL-SPEC-8785C | Dryden PSD | DEF-STAN 00-970

**LLM Girdisi:** `dynamics.json + controller.json + wind_spectrum`

**Script:**
```python
gust_response.py  # 1-cosine gust (Dryden spektrumu); pozisyon/attitude dev.
# H∞ norm: ||T_zw||∞ ≤ γ; gust rejection bandwith
```

**Beklenen Çıktı:** `gust.json: pos_dev_max_m, att_dev_max_deg, recovery_s, gust_rejection_dB`

**✅ Kabul Kriteri:** Gust sonrası pos sapma ≤ 2 m; toparlanma ≤ 5 s

### `WBS 5.5` Ground Effect İleri Uçuş Geçiş Analizi

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 3.3+5.3

**Standart:** Cheeseman-Bennett | Leishman §7

**LLM Girdisi:** `ground_effect.json + fwd_flight.json`

**Script:**
```python
ige_transition.py  # IGE→OGE geçiş profili; optimal kalkış açısı
# P_transition(z) = P_hover × T_OGE/T_IGE(z); min enerji kalkış yörüngesi
```

**Beklenen Çıktı:** `ige_fwd.json: P_takeoff_W, optimal_climb_angle_deg, z_OGE_m, P_profile_W[]`

**✅ Kabul Kriteri:** Kalkış güç bütçesi IGE→OGE geçişi dahil; optimal climb angle hesaplanmış

### `WBS 5.6` Akustik & Gürültü Tahmini (FW-H / BPM) 🔧[TECH-FIX]

**Yazılım:** LLM (Python)  [TECH-FIX]  **|**  **Kaynak:** WBS 3.5

**Standart:** FW-H (Ffowcs Williams-Hawkings 1969) | BPM | ISO 3744 — [TECH+STD fix]

**LLM Girdisi:** `propeller.json + RPM_hover + D_rotor + fwd_flight.json`

**Script:**
```python
noise_model.py  # TECH-FIX: FW-H (Ffowcs Williams-Hawkings) kalınlık+yükleme
# BPM basit model + FW-H düzeltme faktörü: ΔSPL = f(Mach_tip)
# SPL_total = 10×log10(10^(SPL_thickness/10) + 10^(SPL_loading/10))
```

**Beklenen Çıktı:** `noise.json: OASPL_dBA_1m, SPL_thickness_dB, SPL_loading_dB, dominant_freq_Hz`

**✅ Kabul Kriteri:** OASPL ≤ 70 dBA @ 1 m (şehir içi ops)

---
## WBS 6.0 — AŞAMA 6 Yapısal & Termal Tasarım

### `WBS 6.1` Kol (Arm) Kesit Boyutlandırma 📋[STD-FIX]

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 3.9+2.2

**Standart:** MIL-HDBK-5J | ASTM D3039 | EASA SC-VTOL §2301 — [STD: FAR23→SC-VTOL]

**LLM Girdisi:** `thrust_chain.json: T_per_rotor + geometry.json: arm_length_m`

**Script:**
```python
arm_size.py  # M=T_per_rotor×L_arm×n_DLL; σ=M×c/I; I=π(D4-d4)/64
# n_DLL=3.5; MS=σ_ult/σ_max - 1 ≥ 1.5
```

**Beklenen Çıktı:** `arm_sizing.json: material, D_out_mm, t_wall_mm, sigma_max_MPa, MS, I_mm4`

**✅ Kabul Kriteri:** MS ≥ 1.5 @ 3.5g DLL (KK-6); kesit atalet momenti I hesaplanmış

### `WBS 6.2` Motor Montaj Rijitliği & Titreşim İletimi 🆕[NEW]

**Yazılım:** LLM (Python)+scipy  [NEW]  **|**  **Kaynak:** WBS 6.1+3.6

**Standart:** Rao Mechanical Vibrations | ISO 10816 — [NEW: motor mount analysis]

**LLM Girdisi:** `arm_sizing.json + motor.json: weight_g + RPM_max`

**Script:**
```python
mount_stiffness.py  # Motor mount: k_mount ≥ motor_mass × (2π×RPM/60)² × 2
# Titreşim iletim oranı: TR = k_mount/(k_mount - m×ω²)
# Hedef: TR ≤ 0.15 @ RPM_hover
```

**Beklenen Çıktı:** `mount_stiffness.json: k_mount_Nm, TR_at_hover, mount_material, mount_dims_mm`

**✅ Kabul Kriteri:** Titreşim iletim oranı TR ≤ 0.15 @ hover RPM; mount rijitliği hesaplanmış

### `WBS 6.3` Hub Gövde FEA Analizi (CalculiX)

**Yazılım:** CalculiX / FEniCSx  **|**  **Kaynak:** WBS 6.1+2.4

**Standart:** MIL-HDBK-516C §5 | EASA CS-23 Amdt.5

**LLM Girdisi:** `mc.stl + arm_sizing.json`

**Script:**
```python
fea_hub.py  # .inp oluştur: NODE/ELEMENT/BOUNDARY/LOAD; ccx statik+modal
# Yük: T_total×n_DLL vertikal + kol yatay moment
```

**Beklenen Çıktı:** `fea.json: max_stress_MPa, max_defl_mm, nat_freq_Hz[], MS_min, mode_shapes[]`

**✅ Kabul Kriteri:** MS ≥ 1.5; f_nat[0] > 2×RPM_max_Hz (Campbell kriteri)

### `WBS 6.4` Campbell Diyagramı & Rezonans Analizi 🔧[TECH-FIX]

**Yazılım:** LLM (Python)  [TECH-FIX]  **|**  **Kaynak:** WBS 6.3

**Standart:** ISO 10816-3 | PX4 Vibration Guide — [TECH: Hz/RPM format düzeltildi]

**LLM Girdisi:** `fea.json: nat_freq_Hz[] + RPM_range`

**Script:**
```python
campbell.py  # TECH-FIX: frekans formatı düzeltildi
# Harmonikler: f_harm_n = n × (RPM/60)  [Hz cinsinden; DEĞİL RPM]
# Rezonans marjı: |f_nat - f_harm_n| / f_nat ≥ 0.20 (±%20)
# Campbell plot: y=frekans[Hz] vs x=RPM; hatched zones
```

**Beklenen Çıktı:** `campbell.json: critical_RPMs[], safety_margin_pct[], anti_vib_mount_k, imu_vib_g_rms`

**✅ Kabul Kriteri:** Kritik RPM'lerden ≥ %20 uzak; IMU titreşim ≤ 0.3 g RMS

### `WBS 6.5` Motor Termal Analizi 📋[STD-FIX]

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 3.6

**Standart:** IEC 60034-1 | MIL-STD-810H Method 501 — [STD: §514→501 termal metot]

**LLM Girdisi:** `motor.json: P_max, eta + ambient_temp + duty_cycle`

**Script:**
```python
thermal_motor.py  # Q=P_max×(1-η_mot)×duty; R_th=ΔT/Q; T_mot=T_amb+Q×R_th
# T_margin=(T_max-T_mot)/T_max×100 ≥ 20%
```

**Beklenen Çıktı:** `thermal.json: T_motor_C, T_max_C, T_margin_pct, R_th_CW, cooling_method`

**✅ Kabul Kriteri:** T_margin ≥ 20% (KK-10); R_th hesaplanmış; soğutma yöntemi belirlenmiş

### `WBS 6.6` Çevre Koruma — IP Sınıfı & Sıcaklık Aralığı

**Yazılım:** LLM (Spec Parser)  **|**  **Kaynak:** WBS 1.3+3.6

**Standart:** IEC 60529 | MIL-STD-810H | DO-160G §4

**LLM Girdisi:** `regulation.json: ops_env + motor/esc/avionics datasheets`

**Script:**
```python
env_protection.py  # IP sınıfı gereksinim tablosu; ops sıcaklık; nem
# Açık hava urban: IP43; yağmurlu: IP54; su üstü: IP65
```

**Beklenen Çıktı:** `env_prot.json: IP_class, T_ops_min_C, T_ops_max_C, humidity_max_pct, corrosion_class`

**✅ Kabul Kriteri:** IP ≥ 43 (standart açık hava); tüm bileşenler ops sıcaklık aralığında

---
## WBS 7.0 — AŞAMA 7 Uçuş Kontrol & GNC

### `WBS 7.1` 6-DOF Dinamik Model

**Yazılım:** LLM (Python/NumPy)  **|**  **Kaynak:** WBS 2.7+3.6

**Standart:** Mahony 2012 | Stevens & Lewis Aircraft Control | Quan Multicopter Design

**LLM Girdisi:** `mass_budget.json + geometry.json + motor.json`

**Script:**
```python
dynamics_6dof.py  # Newton-Euler; I_xx/yy/zz paralel eksen teoremi
# I_body = I_cm + m×d²; tau_gyro = I_rotor×Ω × dψ/dt
```

**Beklenen Çıktı:** `dynamics.json: I_xx, I_yy, I_zz, m_kg, b_thrust, d_drag, tau_motor, I_rotor`

**✅ Kabul Kriteri:** Atalet tensörü paralel eksen teoremi ile hesaplanmış; gyro terimi dahil

### `WBS 7.2` Motor Mixing Matrix & Kontrol Yapısı  [TECH-FIX] 🔧[TECH-FIX]

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 2.1+7.1

**Standart:** PX4 Mixer | EASA SC-VTOL §2530 — [TECH: cond number check eklendi]

**LLM Girdisi:** `config.json: n_rotors, layout, rotation_dirs[] + dynamics.json`

**Script:**
```python
mixing.py  # TECH-FIX: Condition number kontrolü eklendi
# B_alloc: [F_z, M_roll, M_pitch, M_yaw] = B × [Ω₁²..Ωn²]
# Singularity check: cond(B) < 50; rank(B) == 4
# OEI: B_reduced = B sütun_i silinmiş; rank_OEI ≥ 3
```

**Beklenen Çıktı:** `mixing.json: B_matrix, cond_number, rank, OEI_authority, failsafe_modes[], rotation_dirs[]`

**✅ Kabul Kriteri:** rank(B) = 4; cond(B) < 50; OEI durumunda kontrol otoritesi korunmuş

### `WBS 7.3` LQR / PID Kontrol Tasarımı 🔧[TECH-FIX]

**Yazılım:** Python-control / scipy  **|**  **Kaynak:** WBS 7.1

**Standart:** MIL-F-9490D | ADS-33E-PRF | [TECH: anti-windup eklendi]

**LLM Girdisi:** `dynamics.json + bandwidth_req_Hz`

**Script:**
```python
control_design.py  # Linearize@hover; A,B→LQR; BW≥10Hz; PM≥45°
# Anti-windup: integrator saturation ±I_max; back-calculation
# Bode plot: PM, GM hesabı; step response: overshoot ≤ 10%
```

**Beklenen Çıktı:** `controller.json: Kp/Ki/Kd, anti_windup_limit, LQR_K, bandwidth_Hz, phase_margin_deg, GM_dB`

**✅ Kabul Kriteri:** BW ≥ 10 Hz (KK-9); PM ≥ 45°; GM ≥ 6 dB; anti-windup aktif

### `WBS 7.4` Anti-Windup & Actuator Saturation Yönetimi 🆕[NEW]

**Yazılım:** LLM (Python)  [NEW]  **|**  **Kaynak:** WBS 7.3

**Standart:** Johansen & Fossen 2013 | PX4 MC Rate Control — [NEW]

**LLM Girdisi:** `controller.json + motor.json: RPM_min, RPM_max`

**Script:**
```python
anti_windup.py  # Back-calculation anti-windup
# Saturation: Ω_cmd ∈ [RPM_min, RPM_max]
# Control allocation: redistribute saturated input to feasible rotors
# Priority: altitude > yaw > roll/pitch
```

**Beklenen Çıktı:** `anti_windup.json: windup_limit, saturation_RPM_min, saturation_RPM_max, priority_order`

**✅ Kabul Kriteri:** Integratör sınırları belirlendi; saturasyon öncelik sırası tanımlandı

### `WBS 7.5` İrtifa Kontrolcüsü (Baro + Optical Flow + Lidar) 🆕[NEW]

**Yazılım:** LLM (Python)  [NEW]  **|**  **Kaynak:** WBS 7.5+9.1

**Standart:** PX4 MC Position Control | Mahony — [NEW: baro/optical/lidar fusion]

**LLM Girdisi:** `nav.json + sensor_specs.json + controller.json`

**Script:**
```python
altitude_ctrl.py  # Baro: P→alt; optical flow: vz; lidar: z
# Cascade: alt_error→v_z_cmd→throttle; complementary filter
# alt_rms_target ≤ 0.1m indoor; ≤ 0.2m outdoor
```

**Beklenen Çıktı:** `altitude_ctrl.json: Kp_alt, Ki_alt, Kd_alt, alt_rms_target_m, sensor_fusion_weights`

**✅ Kabul Kriteri:** Alt RMS ≤ 0.1 m indoor (SITL); sensor füzyon ağırlıkları belirlenmiş

### `WBS 7.6` Rüzgar Gustu & Disturbans Reddi

**Yazılım:** LLM (Python+control)  **|**  **Kaynak:** WBS 7.3+5.4

**Standart:** MIL-SPEC-8785C | H∞ robust control

**LLM Girdisi:** `controller.json + gust.json`

**Script:**
```python
disturbance.py  # H∞ disturbance rejection; Dryden PSD gust
# ||T_zw||∞ ≤ γ (γ < 1 → disturbans bastırma)
```

**Beklenen Çıktı:** `gust_ctrl.json: pos_dev_max_m, recovery_s, gust_rejection_dB, Hinf_gamma`

**✅ Kabul Kriteri:** Gust pos sapma ≤ 2 m; recovery ≤ 5 s; γ < 1.0

### `WBS 7.7` EKF Navigasyon & Sensör Füzyonu  [TECH-FIX] 🔧[TECH-FIX]

**Yazılım:** LLM (Python)+filterpy  **|**  **Kaynak:** WBS 7.1

**Standart:** DO-316A | RTCA DO-365 | IEEE AES — [TECH: Q/R matrisleri eklendi, STD: DO-316→DO-316A]

**LLM Girdisi:** `IMU_noise.json + GPS_params.json + baro_noise`

**Script:**
```python
ekf_nav.py  # TECH-FIX: Q_noise ve R_noise matrisleri tam tanımlandı
# Q = diag([σ_acc², σ_gyro², σ_bias²]) — proses gürültüsü
# R = diag([σ_GPS_pos², σ_GPS_vel², σ_baro²]) — ölçüm gürültüsü
# Quaternion normalize: q=q/||q||  her adımda
```

**Beklenen Çıktı:** `nav.json: pos_acc_m, vel_acc_ms, att_acc_deg, Q_matrix, R_matrix, update_rate_Hz`

**✅ Kabul Kriteri:** Pozisyon ≤ 0.5 m; Yaw ≤ 2°; Q ve R matrisleri tam tanımlı

### `WBS 7.8` Geofencing & Otopilot Güvenlik Mantığı

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 1.3+7.3

**Standart:** EASA AMC RPAS.1309 | DO-365 | JARUS SORA OSO#06

**LLM Girdisi:** `regulation.json + mission_profile.json`

**Script:**
```python
geofence.py  # Silindirik/poligon geofence; RTL trigger; OBC watchdog
# RC-loss: t_timeout=1.0s → RTL; low-bat: E<20% → RTL; geofence breach → RTL
```

**Beklenen Çıktı:** `geofence.json: fence_type, RTL_alt_m, failsafe_chain[], RC_timeout_s, low_bat_pct`

**✅ Kabul Kriteri:** RTL tüm senaryolarda ≤ 3 s; failsafe_chain tüm arıza durumlarını kapsar

### `WBS 7.9` Yazılım Mimarisi (PX4/ArduPilot Özelleştirme)

**Yazılım:** LLM (Python+YAML)  **|**  **Kaynak:** WBS 7.2+7.3

**Standart:** PX4 Dev Guide v1.14 | ArduPilot Docs | MAVLink 2.0

**LLM Girdisi:** `config.json + controller.json + mixing.json`

**Script:**
```python
fw_config.py  # PX4 param set; uXRCE-DDS topic; custom mixer YAML
# MAVLink handshake test; param upload verify; mixer validate
```

**Beklenen Çıktı:** `firmware_config.json: fw_version, param_file, mixer_file, mavlink_OK, params_count`

**✅ Kabul Kriteri:** Firmware parametreleri upload edilmiş; MAVLink handshake OK

---
## WBS 8.0 — AŞAMA 8 Haberleşme & Datalink Sistemi

### `WBS 8.1` RC Link Seçimi & Menzil Hesabı

**Yazılım:** LLM (Spec Parser)  **|**  **Kaynak:** WBS 1.3+1.1

**Standart:** ETSI EN 300 328 | FCC Part 15 | DO-160G §20

**LLM Girdisi:** `regulation.json + mission_profile.json: range_km`

**Script:**
```python
rc_link.py  # Link budget: EIRP - FSPL - margin ≥ sensitivity
# ELRS: 2.4GHz 100mW → 3 km VLOS; Crossfire: 868MHz 1W → 10 km BVLOS
```

**Beklenen Çıktı:** `rc_link.json: protocol, freq_MHz, tx_power_mW, range_km, latency_ms, RSSI_threshold`

**✅ Kabul Kriteri:** RC menzil ≥ ops_menzil × 1.5; gecikme ≤ 30 ms

### `WBS 8.2` Telemetri & C2 Datalink Tasarımı 📋[STD-FIX]

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 1.3

**Standart:** JARUS SORA OSO#10 | DO-365 | EUROCAE ED-269 — [STD: DO-316→ED-269]

**LLM Girdisi:** `regulation.json: SAIL_level + mission_profile.json`

**Script:**
```python
c2_link.py  # MAVLink 2.0/MAVSDK; link margin; C2 availability
# BVLOS: LTE + 915 MHz yedek; heartbeat timeout ≤ 5 s
```

**Beklenen Çıktı:** `c2_link.json: protocol, band_MHz, data_rate_kbps, latency_ms, availability_pct`

**✅ Kabul Kriteri:** C2 gecikme ≤ 200 ms (BVLOS); availability ≥ 99.9%

### `WBS 8.3` Haberleşme Güvenliği (Şifreleme & Spoofing Koruması) 🆕[NEW]

**Yazılım:** LLM (Python)  [NEW]  **|**  **Kaynak:** WBS 8.2+1.3

**Standart:** EUROCAE ED-269 | JARUS SORA OSO#10 | NIST SP 800-38A — [NEW]

**LLM Girdisi:** `c2_link.json + regulation.json: SAIL_level`

**Script:**
```python
comm_security.py  # AES-128/256 MAVLink şifrelemesi; GPS anti-spoofing
# HMAC imzalama; replay attack koruması (timestamp+nonce)
# GPS: çoklu frekans (L1+L5) spoofing tespiti
```

**Beklenen Çıktı:** `comm_security.json: encryption_type, HMAC_flag, GPS_anti_spoof, auth_method`

**✅ Kabul Kriteri:** AES-128 minimum; HMAC aktif; GPS multi-freq spoofing tespiti

### `WBS 8.4` Veri Kayıt & Telemetri Sistemi (Black Box)

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 7.1+7.3

**Standart:** DO-160G §9 | PX4 uLog Spec | EASA DVR Req.

**LLM Girdisi:** `dynamics.json + controller.json + avionics spec`

**Script:**
```python
datalog.py  # ulog/DataFlash format; ≥100 Hz; SD boyutu
# Zorunlu loglar: IMU, GPS, attitude, ESC_status, battery, RC, modes
```

**Beklenen Çıktı:** `datalog.json: log_format, rate_Hz, duration_h, storage_GB, mandatory_params[]`

**✅ Kabul Kriteri:** ≥250 parametre @ 100 Hz; depolama ≥ 10 h; mandatory_params tam

### `WBS 8.5` GCS (Ground Control Station) Kurulum & Test

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 7.8+8.2

**Standart:** JARUS SORA OSO#11 | QGC Docs | MAVLink 2.0

**LLM Girdisi:** `c2_link.json + geofence.json + mission_profile.json`

**Script:**
```python
gcs_setup.py  # QGC/Mission Planner bağlantı; geofence yükle; preflight check
# MAVLink heartbeat ≤ 1 Hz; mission upload verify; parameter sync
```

**Beklenen Çıktı:** `gcs.json: sw_version, connection_OK, geofence_loaded, telemetry_latency_ms, params_synced`

**✅ Kabul Kriteri:** GCS bağlantısı ≤ 500 ms; geofence yüklendi; parametreler senkronize

### `WBS 8.6` Hava Sahası Entegrasyonu — UTM/U-Space

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 1.3

**Standart:** ASTM F3411-22a | EASA U-Space Reg. 2021/664 | ICAO Annex 2

**LLM Girdisi:** `regulation.json + mission_profile.json: route`

**Script:**
```python
utm_integration.py  # ASTM F3411 RID; flight plan submission; NOTAM
# UAS ID broadcast: 802.11 Wi-Fi / BT5; USS API endpoint
```

**Beklenen Çıktı:** `utm.json: RID_compliant, flight_plan_id, USS_endpoint, BVLOS_auth, NOTAM_checked`

**✅ Kabul Kriteri:** Remote ID aktif; uçuş planı onaylı; NOTAM kontrolü yapılmış

---
## WBS 9.0 — AŞAMA 9 Sensör Kalibrasyon & Payload Entegrasyonu

### `WBS 9.1` Sensör Kalibrasyon Prosedürü  [NEW] 🆕[NEW]

**Yazılım:** LLM (Python)+MAVLink  **|**  **Kaynak:** WBS 7.9

**Standart:** PX4 Sensor Calib. | DO-160G §19 | IEEE 1554 — [NEW: kalibrasyon prosedürü]

**LLM Girdisi:** `firmware_config.json + sensor_specs.json`

**Script:**
```python
sensor_calib.py  # IMU: 6-pozisyon kalibrasyon (Allen Variance)
# Manyetometre: elipsoid fit (12-param least squares)
# Baro: sıcaklık kompanzasyonu; AHRS sıfırlama
# MAVLink: MAV_CMD_PREFLIGHT_CALIBRATION
```

**Beklenen Çıktı:** `sensor_calib.json: IMU_bias[], IMU_scale[], mag_ellipsoid_params[], baro_offset, allan_dev`

**✅ Kabul Kriteri:** IMU Allan deviation < 0.1 °/√h; mag cal residual < 20 mGauss

### `WBS 9.2` Payload Tanımlama & Entegrasyon Arayüzü

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 1.1+2.7

**Standart:** EASA SC-VTOL §2550 | MIL-STD-1760 | DO-160G §1

**LLM Girdisi:** `mission_profile.json: payload_type + mass_budget.json`

**Script:**
```python
payload_interface.py  # Mekanik montaj + elektrik arayüz + CG etkisi
# Δcg = m_payload × (x_payload - cg_x) / MTOW ≤ 3 mm
```

**Beklenen Çıktı:** `payload.json: mass_kg, cg_offset_mm, power_W, data_interface, mount_type, Δcg_mm`

**✅ Kabul Kriteri:** Payload montajı sonrası Δcg ≤ 3 mm; elektrik arayüz tanımlanmış

### `WBS 9.3` Gimbal & Kamera Sistemi Tasarımı

**Yazılım:** LLM (Python+Spec)  **|**  **Kaynak:** WBS 9.2+6.4

**Standart:** MIL-STD-810H Method 514 | Sony/DJI gimbal specs

**LLM Girdisi:** `payload.json + campbell.json: imu_vib_g_rms`

**Script:**
```python
gimbal_design.py  # 3-axis stabilizasyon; servo tork = I_gimbal×α_max
# Stabilizasyon BW ≥ 50 Hz; isolation: ≥ 30 dB @ rotor harmonikleri
```

**Beklenen Çıktı:** `gimbal.json: axes, torque_Nm, stab_BW_Hz, isolation_dB, camera_spec, MAVLink_ctrl`

**✅ Kabul Kriteri:** Gimbal stab ≤ 0.01° RMS @ hover; 3-axis; MAVLink kamera kontrol

### `WBS 9.4` LiDAR / Engellerden Kaçınma Sistemi

**Yazılım:** LLM (Python+ROS2)  **|**  **Kaynak:** WBS 2.4+1.1

**Standart:** DO-365 BVLOS | ASTM F3322-18 | ISO 10218-1

**LLM Girdisi:** `geometry.json + mission_profile.json: ops_env`

**Script:**
```python
obstacle_avoid.py  # LiDAR pointcloud; ROS2 costmap2D; velocity obstacle
# Güvenli durak mesafesi: d_safe = V_max × t_brake + d_margin
```

**Beklenen Çıktı:** `lidar.json: range_m, FOV_deg, rate_Hz, ros2_topic, d_safe_m, obstacle_margin_m`

**✅ Kabul Kriteri:** Engel tespiti ≥ 10 m önce; d_safe_m hesaplanmış

### `WBS 9.5` Uçuş Öncesi Kontrol Listesi Otomasyonu

**Yazılım:** LLM (Python)+MAVLink  **|**  **Kaynak:** WBS 7.9+8.5+4.2

**Standart:** EASA AMC RPAS.1309 | FAA UAS Safety | PX4 Arming Checks

**LLM Girdisi:** `firmware_config.json + gcs.json + battery.json + sensor_calib.json`

**Script:**
```python
preflight.py  # MAVLink: GPS≥6sat, HDOP≤2.0, bat≥20%, cal_OK
# arming_check bitmask: 0x1FF (tüm kontroller)
# Mekanik: prop tork kontrolü; motor test her motor sırayla
```

**Beklenen Çıktı:** `preflight.json: checklist_items[], pass_fail[], arming_ready, motor_test_OK`

**✅ Kabul Kriteri:** Tüm preflight PASS olmadan arm engellenmeli; motor test OK

---
## WBS 10.0 — AŞAMA 10 SITL & HITL Simülasyonu

### `WBS 10.1` Gazebo Multirotor SDF Model Üretimi

**Yazılım:** Gazebo Harmonic + ROS 2  **|**  **Kaynak:** WBS 2.4+7.1

**Standart:** Gazebo Harmonic Docs | PX4 SITL Guide v1.14

**LLM Girdisi:** `mc.stl + dynamics.json + motor.json`

**Script:**
```python
gen_sdf.py  # STL→SDF; inertia tensor; rotor_plugin; sensor plugins
# rotor_plugin: b_thrust, d_drag, time_constant_ms, max_RPM
```

**Beklenen Çıktı:** `mc_model.sdf + package.xml + model.config`

**✅ Kabul Kriteri:** Gazebo modeli hatasız yüklenmeli; hover kararlı

### `WBS 10.2` SITL Hover & Attitude Kararlılık Testi

**Yazılım:** PX4/ArduPilot SITL  **|**  **Kaynak:** WBS 10.1+7.3+7.5

**Standart:** PX4 QA | DO-178C Level C

**LLM Girdisi:** `mc_model.sdf + controller.json + altitude_ctrl.json`

**Script:**
```python
sitl_hover.py  # ARM→OFFBOARD→hover 60s; attitude+altitude log
# roll_rms, pitch_rms, yaw_rms, alt_rms hesabı
```

**Beklenen Çıktı:** `sitl_hover.json: roll_rms_deg, pitch_rms_deg, yaw_rms_deg, alt_rms_m, hover_s`

**✅ Kabul Kriteri:** Roll/Pitch RMS ≤ 1.0°; Yaw RMS ≤ 2.0°; Alt RMS ≤ 0.1 m (KK-11)

### `WBS 10.3` SITL Manevra & Yol Takip Testi

**Yazılım:** PX4 SITL + MAVLink  **|**  **Kaynak:** WBS 10.2

**Standart:** RTCA DO-365 | JARUS SORA §4

**LLM Girdisi:** `sitl_hover.json + waypoint_mission.json`

**Script:**
```python
sitl_mission.py  # Waypoint görev; cross_track_error; tamamlama
# 10 waypoint; speed 5 m/s; altitude hold ± 1 m
```

**Beklenen Çıktı:** `sitl_mission.json: cross_track_err_m, speed_err_ms, alt_err_m, completion_flag`

**✅ Kabul Kriteri:** Cross-track ≤ 1.0 m; görev tamamlama = True; alt_err ≤ 1.0 m

### `WBS 10.4` Rüzgar & Disturbans SITL Testi

**Yazılım:** PX4 SITL + Gazebo Wind  **|**  **Kaynak:** WBS 10.2+7.6

**Standart:** MIL-SPEC-8785C | Gazebo Wind Plugin

**LLM Girdisi:** `sitl_hover.json + gust_ctrl.json`

**Script:**
```python
sitl_wind.py  # Gazebo wind plugin; gust 5 m/s @ 45°; pos/att log
# von Kármán turbulence spectrum opsiyonel
```

**Beklenen Çıktı:** `sitl_wind.json: pos_dev_max_m, att_dev_max_deg, recovery_s, wind_speed_ms`

**✅ Kabul Kriteri:** Gust sonrası pos sapma ≤ 2 m; recovery ≤ 5 s (KK gust)

### `WBS 10.5` Monte Carlo SITL Analizi (Parametre Belirsizliği) 🆕[NEW]

**Yazılım:** LLM (Python)+PX4  [NEW]  **|**  **Kaynak:** WBS 10.2+7.1

**Standart:** MIL-HDBK-17F §2 | Monte Carlo Methods — [NEW]

**LLM Girdisi:** `dynamics.json + controller.json + sensor_noise_params`

**Script:**
```python
monte_carlo.py  # N=100 simülasyon; parametre pertürbasyon ±10%
# mass_pert ±5%, I_pert ±10%, b_thrust_pert ±8%
# Çıktı: roll_rms dağılımı; %95 güven aralığı
```

**Beklenen Çıktı:** `monte_carlo.json: N_runs, param_perturbations{}, roll_rms_p95, converge_flag`

**✅ Kabul Kriteri:** Roll RMS p95 ≤ 1.5°; tüm N çalıştırma tamamlanmış

### `WBS 10.6` HITL & Gerçek Donanım Doğrulama

**Yazılım:** HITL FC + PC  **|**  **Kaynak:** WBS 10.3

**Standart:** DO-160G §14 | PX4 HITL Guide

**LLM Girdisi:** `Gerçek FC + sitl_mission.json`

**Script:**
```python
hitl_setup.py  # FC→USB HITL; sensor sim in-loop; latency ölç
# MAVLink heartbeat; HITL_SENSOR mesajı; latency ≤ 20 ms
```

**Beklenen Çıktı:** `hitl.json: latency_ms, sensor_noise_impact, ctrl_authority_flag, heartbeat_OK`

**✅ Kabul Kriteri:** HITL gecikme ≤ 20 ms; FC SITL ile tutarlı

---
## WBS 11.0 — AŞAMA 11 Fiziksel Test & Doğrulama

### `WBS 11.1` Statik İtki Testi (Test Standı)

**Yazılım:** Python DAQ + loadcell  **|**  **Kaynak:** WBS 3.9

**Standart:** ASTM F3002 §8 | SAE ARP5247 | ISO 3744

**LLM Girdisi:** `propeller.json + motor.json + bemt.json`

**Script:**
```python
bench_test.py  # Loadcell+tachometer+power meter; CT/CQ/FM@5 RPM noktası
# FFT: 1P harmonik; BEMT karşılaştırma
```

**Beklenen Çıktı:** `bench.json: T_meas_N[], P_meas_W[], FM_meas[], CT_meas, bemt_err_pct`

**✅ Kabul Kriteri:** FM_meas ≥ 0.60; BEMT hata ≤ %10; 5 RPM noktası (KK-2)

### `WBS 11.2` Pervane Balans Doğrulama Testi

**Yazılım:** IMU log + tachometer  **|**  **Kaynak:** WBS 3.8+11.1

**Standart:** ISO 1940-1 | PX4 Vibration

**LLM Girdisi:** `balance_procedure.md + RPM_hover`

**Script:**
```python
balance_verify.py  # IMU FFT @ RPM_hover; 1P harmonik; ISO 1940 G1 doğrulama
# U_res = m × e_meas; U_perm(G1, RPM) = 9549×G1/RPM
```

**Beklenen Çıktı:** `balance_verify.json: vib_1P_g, vib_rms_g, U_residual_g_mm, ISO1940_OK`

**✅ Kabul Kriteri:** 1P ≤ 0.05 g; RMS ≤ 0.1 g; ISO 1940 G1 karşılanmış

### `WBS 11.3` Çevre Testi (DO-160G Kategorileri) 🆕[NEW]

**Yazılım:** Test odası + Python DAQ  [NEW]  **|**  **Kaynak:** WBS 6.6+1.3

**Standart:** DO-160G §4,§8,§14,§20 — [NEW: çevre testi eklendi]

**LLM Girdisi:** `env_prot.json + regulation.json: DO160_class`

**Script:**
```python
env_test.py  # DO-160G §4 sıcaklık: -20°C..+55°C siklus
# §8 titreşim: 5-2000 Hz random; §14 nem: %95 @ 40°C
# Her test sonrası işlevsellik doğrulama
```

**Beklenen Çıktı:** `env_test.json: temp_test_pass, vib_test_pass, humidity_test_pass, DO160_class`

**✅ Kabul Kriteri:** Tüm DO-160G kategorileri PASS; işlevsellik her test sonrası OK

### `WBS 11.4` Bağlı (Tethered) Hover Testi

**Yazılım:** Gerçek donanım + flight log  **|**  **Kaynak:** WBS 11.1+10.2

**Standart:** EASA AMC RPAS.1309 | ARP4761 §C

**LLM Girdisi:** `controller.json + mc_model`

**Script:**
```python
tethered.py  # 120 s bağlı hover; IMU log; vibrasyon; bat drain
# Tether kuvveti ≤ 0.05 × MTOW × g (serbest hover yaklaşımı)
```

**Beklenen Çıktı:** `tethered.json: hover_stable_s, vib_g_rms, bat_drain_Ah, tether_force_N`

**✅ Kabul Kriteri:** Kararlı hover ≥ 120 s; IMU ≤ 0.3 g RMS; tether kuvveti küçük

### `WBS 11.5` Serbest Uçuş & Performans Doğrulama

**Yazılım:** Uçuş log + Python  **|**  **Kaynak:** WBS 11.4+1.2

**Standart:** FAA AC 21.17-1A | DO-160G | STANAG 4703

**LLM Girdisi:** `tethered.json + requirements.json`

**Script:**
```python
flight_verify.py  # t_hover, V_max, range, payload; log analizi
```

**Beklenen Çıktı:** `flight.json: t_hover_meas_min, V_max_meas_ms, payload_OK, range_km_meas`

**✅ Kabul Kriteri:** Tüm performans ≤ %5 toleransla karşılanmış (KK-3, KK-12)

### `WBS 11.6` FMEA / FTA Güvenlik Değerlendirmesi

**Yazılım:** LLM (Python)+FTA  **|**  **Kaynak:** WBS 11.5

**Standart:** ARP4761A | JARUS SORA OSO tablosu | ED-135

**LLM Girdisi:** `system_arch.json + failure_modes.json`

**Script:**
```python
fmea_fta.py  # FMEA: her bileşen × şiddet × olasılık × tespit
# FTA: top event 'Uncontrolled landing' → minimal cut sets
# RPN = Severity × Occurrence × Detection
```

**Beklenen Çıktı:** `safety.json: FMEA_table[], FTA_probability, RPN_max, SAIL_compliance_flag`

**✅ Kabul Kriteri:** P(katastrofik) ≤ 10⁻⁷/saat; RPN_max ≤ 100; SAIL_compliance: True

---
## WBS 12.0 — AŞAMA 12 Üretim & Montaj

### `WBS 12.1` Bileşen Tedarik & BOM Yönetimi

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 6.1+3.6+3.7+4.2+4.5

**Standart:** AS9102 | IPC-7711 | ISO 9001:2015

**LLM Girdisi:** `arm_sizing+motor+esc+battery+avionics+cables JSONs`

**Script:**
```python
bom_gen.py  # Bill of Materials; tedarikçi; stok; maliyet; lead time
# BOM hierarchy: L0 sistem → L1 alt-sistem → L2 bileşen
```

**Beklenen Çıktı:** `bom.json: items[], quantities[], suppliers[], unit_cost_USD[], lead_time_days[], total_cost`

**✅ Kabul Kriteri:** BOM tüm bileşenleri kapsar; maliyet bütçe dahilinde; lead time analizi

### `WBS 12.2` Montaj Sırası & Prosedür Üretimi

**Yazılım:** LLM (Markdown üretimi)  **|**  **Kaynak:** WBS 12.1+2.5

**Standart:** IPC-7711 | AS9100D | MIL-HDBK-516C §1

**LLM Girdisi:** `bom.json + geometry.json + arm_design.json`

**Script:**
```python
assembly_proc.py  # Adım adım montaj; tork değerleri; ESD önlemleri
# CFRP: toz koruması; batarya: yangın önlemi; elektronik: ESD koruma
```

**Beklenen Çıktı:** `assembly_procedure.md: adımlar[], tork_specs[], ESD_precautions[], test_checkpoints[]`

**✅ Kabul Kriteri:** Montaj prosedürü eksiksiz; tork değerleri Nm'de; ESD önlemleri belirtilmiş

### `WBS 12.3` Kalite Kontrol & Kabul Testi Prosedürü

**Yazılım:** LLM (Python+Prosedür)  **|**  **Kaynak:** WBS 12.2+11.5

**Standart:** AS9102 | ISO 9001:2015 | DO-160G

**LLM Girdisi:** `bom.json + requirements.json + all_KK_results`

**Script:**
```python
qa_acceptance.py  # QC kontrol listesi; FOD kontrolü; elektrik test
# Continuity test; isolation test; functional test sırası
```

**Beklenen Çıktı:** `qa_report.json: inspections[], pass_fail[], nonconformance[], FOD_check`

**✅ Kabul Kriteri:** Tüm kabul testleri PASS; nonconformance = 0; FOD kontrolü OK

---
## WBS 13.0 — AŞAMA 13 MDAO Optimizasyon Döngüsü

### `WBS 13.1` OpenMDAO Problem Tanımı & Bağlantı Şeması

**Yazılım:** OpenMDAO + Python  **|**  **Kaynak:** WBS 1-12 tümü

**Standart:** OpenMDAO 3.x Docs | MDAO metodoloji

**LLM Girdisi:** `Tüm WBS 1-12 JSON çıktıları`

**Script:**
```python
mdao_setup.py  # IndepVarComp; ExecComp; connections; SLSQP driver
# Design vars: D_rotor, n_rotors, S_battery, K_lqr
# Constraints: all 12 KK; Objective: min(MTOW) or max(endurance)
```

**Beklenen Çıktı:** `mdao_problem.json: design_vars[], constraints[], objectives[], connections[], driver`

**✅ Kabul Kriteri:** Convergence ≤ 1e-6; tüm bağlantılar aktif; constraints feasible

### `WBS 13.2` Otomatik KK Döngüsü & Geri Besleme

**Yazılım:** LLM (Python+OpenMDAO)  **|**  **Kaynak:** WBS 13.1

**Standart:** OpenMDAO | Pydantic v2

**LLM Girdisi:** `mdao_problem.json + all_KK_results`

**Script:**
```python
kk_loop.py  # Pydantic tüm şemalar; fail→WBS geri dön; max_iter=5
# Eskalasyon: iter≥5 → escalation_report.json → human engineer
```

**Beklenen Çıktı:** `kk_summary.json: kk1..kk12_pass[], iteration_count, converged_flag, escalation_flag`

**✅ Kabul Kriteri:** Tüm 12 KK PASS; convergence ≤ 5 iterasyon

### `WBS 13.3` Sensitivite Analizi  [NEW] 🆕[NEW]

**Yazılım:** LLM (Python)+OpenMDAO  **|**  **Kaynak:** WBS 13.1

**Standart:** OpenMDAO total_derivatives | Saltelli 2008 FAST — [NEW]

**LLM Girdisi:** `mdao_problem.json + design_vars[]`

**Script:**
```python
sensitivity.py  # Toplam türev (total_derivatives) analizi
# dObjective/dDesignVar; FAST (Fourier Amplitude Sensitivity Test)
# Sonuç: hangi parametre sonucu en çok etkiler
```

**Beklenen Çıktı:** `sensitivity.json: dObj_dVar{}, S1_indices{}, ST_indices{}, critical_vars[]`

**✅ Kabul Kriteri:** Kritik tasarım değişkenleri belirlendi; sensitivite indeksleri hesaplandı

### `WBS 13.4` Pareto Analizi & Tasarım Uzayı Keşfi

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 13.1+13.3

**Standart:** NSGA-II Deb 2002 | pymoo | OpenMDAO pyOptSparse

**LLM Girdisi:** `mdao_problem.json + design_space_bounds`

**Script:**
```python
pareto.py  # NSGA-II: T/W vs endurance Pareto frontier
# pymoo: minimize(MTOW, -endurance); subject to all KK constraints
```

**Beklenen Çıktı:** `pareto.json: frontier_points[], selected_point{}, design_vars_optimal[], justification`

**✅ Kabul Kriteri:** Pareto sınırı ≥ 20 nokta; seçilen nokta tüm KK'ları sağlıyor

---
## WBS 14.0 — AŞAMA 14 LLM Sentez & Teknik Rapor

### `WBS 14.1` Yönetici Özeti & KK Tablosu

**Yazılım:** LLM (NLP)  **|**  **Kaynak:** WBS 13.2

**Standart:** AIAA/AHS Raporlama | EASA DVR Format

**LLM Girdisi:** `kk_summary.json + tüm WBS çıktıları`

**Script:**
```python
report_exec.py  # Tasarım amacı; KK özet tablo; kritik bulgular
# 1 sayfa; tablo: KK kodu | değer | sınır | durum (✅/❌)
```

**Beklenen Çıktı:** `Yönetici Özeti (1 sayfa) + KK Tablosu (12+1 satır = tüm KK)`

**✅ Kabul Kriteri:** Tüm KK PASS; rapor tutarlı ve özlü

### `WBS 14.2` Sistem Tasarım Bölümleri (Bölüm 1-5)

**Yazılım:** LLM (NLP)  **|**  **Kaynak:** WBS 1-12

**Standart:** AIAA Paper Format | EASA DVR §3

**LLM Girdisi:** `Tüm faz JSON çıktıları WBS 1-12`

**Script:**
```python
report_sections.py  # Jinja2 şablon; sayısal tablo; görseller
# Her bölüm ilgili JSON'dan otomatik populate
# Şekil: BEMT polar, CT/CQ, Campbell, CG zarf, kontrol bode
```

**Beklenen Çıktı:** `Bölüm 1-5 Markdown: Görev/Konfig/İtki+Güç/Aerodinamik+Yapı/GNC+Test`

**✅ Kabul Kriteri:** Her bölüm JSON ile kaynaklandırılmış; görseller dahil

### `WBS 14.3` FMEA Tablosu & Güvenlik Bölümü

**Yazılım:** LLM (NLP)  **|**  **Kaynak:** WBS 11.6+1.3

**Standart:** ARP4761A | JARUS SORA | EUROCAE ED-135

**LLM Girdisi:** `safety.json + fmea.json + regulation.json`

**Script:**
```python
report_safety.py  # FMEA tablo; FTA ağacı; SORA OSO compliance tablosu
# FMEA: her satır = bileşen, arıza modu, etkisi, şiddet, RPN
```

**Beklenen Çıktı:** `Güvenlik Bölümü: FMEA + FTA + SORA OSO compliance matrix`

**✅ Kabul Kriteri:** P(katastrofik) < 10⁻⁷; SAIL compliance belgesi tam

### `WBS 14.4` Pydantic Final Doğrulama & JSON Paket 🔧[TECH-FIX]

**Yazılım:** LLM (Python/Pydantic)  **|**  **Kaynak:** WBS 1-13

**Standart:** Pydantic v2 | JSON Schema | [TECH: cross-validation eklendi]

**LLM Girdisi:** `Tüm faz JSON çıktıları`

**Script:**
```python
final_validate.py  # FinalDesignSchemaMC; tüm alan + cross-check
# Cross-check: T_total = n_rotors × T_per_rotor ± 1%
# Cross-check: E_Wh / V_nom × 1000 = C_mAh ± 2%
```

**Beklenen Çıktı:** `final_design.json (validation_passed: True, all_kk_passed: True, cross_checks: True)`

**✅ Kabul Kriteri:** Pydantic doğrulama hatasız; cross-check'ler geçildi

### `WBS 14.5` PDF/Word Rapor İhracı & Arşivleme

**Yazılım:** LLM (Python)  **|**  **Kaynak:** WBS 14.1-14.3

**Standart:** EASA DVR Req. | DO-178C Traceability | ISO 9001:2015 §7.5

**LLM Girdisi:** `Tüm rapor bölümleri + görseller`

**Script:**
```python
export_report.py  # reportlab/python-docx; EASA DVR format
# Versiyon: MAJOR.MINOR.PATCH; git tag; SHA256 hash
```

**Beklenen Çıktı:** `MultiCopter_Design_Report_v1.0.0.pdf + .docx + arşiv.zip + SHA256.txt`

**✅ Kabul Kriteri:** Rapor EASA DVR formatına uygun; SHA256 hash ile bütünlük doğrulandı

---
## 🔄 MDAO GERİ-BESLEME DÖNGÜSÜ v3

```python
# v3 — Tutarsız geri dönüş adresleri düzeltildi
MDAO_TABLE = {
    "KK-1": {"return_to": ["WBS 3.2", "WBS 3.9"], "action": "Rotor çapı +5%; MTOW azalt"},
    "KK-3": {"return_to": ["WBS 4.2", "WBS 4.7"], "action": "Batarya kapasitesi artır"},  # [FIXED]
    "KK-6": {"return_to": ["WBS 6.1", "WBS 6.3"], "action": "Kol kalınlığı; FEA tekrar"},  # [FIXED]
    "KK-9": {"return_to": ["WBS 7.3", "WBS 7.2"], "action": "LQR Q artır; anti-windup"},  # [FIXED]
    "KK-11":{"return_to": ["WBS 7.3", "WBS 7.5", "WBS 10.2"], "action": "PID+altitude_ctrl"}, # [FIXED]
}
iteration = 0
while not all_kk_passed and iteration < 5:
    for kk in failed_kks:
        for wbs_addr in MDAO_TABLE[kk]['return_to']:
            execute_wbs(wbs_addr)
    update_kk_summary()
    iteration += 1
if iteration >= 5:
    generate_escalation_report()
```

---
## ✅ 12 KALİTE KAPISI — v3 (Güncellenmiş Standartlar)

| KK | Parametre | Sınır | Standart (v3) | v3 Değişiklik |
|----|-----------|-------|--------------|--------------|
| KK-1 | TW_ratio | ≥ 2.0 | Raymer §17 | NDARC | — |
| KK-2 | FM (BEMT Glauert) | ≥ 0.60 | Leishman §3 | [TECH] Glauert iter düzeltildi |
| KK-3 | t_hover_min | ≥ end×1.2 | ASTM F3005 | [FIXED] WBS 4.2+4.7 |
| KK-4 | DL_Nm2 | ≤ 300 N/m² | NDARC | — |
| KK-5 | PL_NW | ≥ 8 N/W | NDARC | — |
| KK-6 | MS_structural | ≥ 1.5 | SC-VTOL §2301 | [STD] FAR23→SC-VTOL; [FIXED] WBS 6.1+6.3 |
| KK-7 | cg_deviation_mm | ≤ 5 mm | EASA SC-VTOL §2510 | — |
| KK-8 | s/D spacing | ≥ 1.1 | Leishman §5 | — |
| KK-9 | bandwidth_Hz | ≥ 10 Hz | ADS-33E-PRF | [STD] MIL-F-9490D+ADS-33E; [FIXED] WBS 7.3+7.2 |
| KK-10 | T_motor_margin_pct | ≥ 20% | IEC 60034-1 | — |
| KK-11 | SITL roll_rms | ≤ 1.0° | PX4 QA | DO-178C | [FIXED] WBS 7.3+7.5+10.2 |
| KK-12 | V_max_ms | ≥ V_max_req | STANAG 4703 | — |

---
## 📦 PYDANTIC FINAL ŞEMA v3

```python
from pydantic import BaseModel, Field, model_validator
from typing import List

class FinalDesignMCv3(BaseModel):
    aircraft_name: str; n_rotors: int = Field(..., ge=4)
    MTOW_kg: float = Field(..., gt=0)
    TW_ratio: float = Field(..., ge=2.0)          # KK-1
    FM: float = Field(..., ge=0.60, le=0.85)       # KK-2 [Glauert iter]
    t_hover_min: float                              # KK-3 >= end*1.2
    DL_Nm2: float = Field(..., le=300)              # KK-4
    PL_NW: float = Field(..., ge=8.0)              # KK-5
    MS_structural: float = Field(..., ge=1.5)       # KK-6 [SC-VTOL]
    cg_deviation_mm: float = Field(..., le=5.0)     # KK-7
    spacing_ratio: float = Field(..., ge=1.1)       # KK-8
    Q_yaw_imbalance_Nm: float = Field(..., le=0.01) # [NEW]
    bandwidth_Hz: float = Field(..., ge=10.0)       # KK-9
    T_motor_margin_pct: float = Field(..., ge=20.0) # KK-10
    sitl_roll_rms_deg: float = Field(..., le=1.0)   # KK-11
    V_max_ms: float                                 # KK-12
    endurance_req_min: float
    all_kk_passed: bool = True
    cross_checks_passed: bool = True
    validation_passed: bool = True

    @model_validator(mode='after')
    def cross_validate(self):
        assert self.t_hover_min >= self.endurance_req_min * 1.2, 'KK-3 fail'
        return self
```

---
## 🛠️ KURULUM

```bash
pip install aerosandbox neuralfoil openmdao pydantic scipy numpy pandas
pip install filterpy python-control matplotlib jinja2 reportlab pymoo
pip install cadquery  # kol/motor mount CAD
# OpenVSP: https://openvsp.org/download.php (Python 3.11/3.13)
# Gazebo Harmonic: https://gazebosim.org
# PX4 v1.14: https://github.com/PX4/PX4-Autopilot
# CalculiX: apt install calculix-ccx
```

---
*MultiCopter WBS v3.0 — 87 Görev | 32 Hata Düzeltildi | 12 Yeni Görev | Nisan 2026*