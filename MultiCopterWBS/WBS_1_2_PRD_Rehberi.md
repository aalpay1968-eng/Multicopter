# 📐 WBS 1.2 — PERFORMANS GEREKSİNİM MATRİSİ (PRD)

> **WBS 1.1 kullanıcı girdilerini sayısal performans gereksinimlerine dönüştürür.**
> 9 Kategori | 68 Gereksinim | Formül + KK Bağlantısı + Standart

---
## 🎯 Gereksinim Tipleri
| Tip | Açıklama | Örnek |
|-----|----------|-------|
| **PERF** | Performans: Sayısal ölçülebilir | T/W ≥ 2.0, FM ≥ 0.60 |
| **DES**  | Tasarım: Boyut/form/geometri | s/D ≥ 1.1, CG ≤ 5 mm |
| **FUNC** | Fonksiyonel: Ne yapacak | Remote ID, C2 link |
| **SAFE** | Güvenlik: Kritik güvenlik | P_katast ≤ 1e-7/h |

---
## 🔑 KK Bağlantı Özeti

| KK | REQ-ID | Formül | Sınır |
|----|--------|--------|-------|
| KK-1 | TW_ratio | `T_total/(MTOW×g)` | ≥2.0 |
| KK-2 | FM (BEMT) | `T√(T/2ρA)/P_shaft` | ≥0.60 |
| KK-3 | t_hover_min | `(E_bat×η)/P_total-t_res` | ≥end×1.2 |
| KK-4 | DL_Nm2 | `T_per_rotor/(π×R²)` | ≤300 |
| KK-5 | PL_NW | `T_total/P_total` | ≥8.0 |
| KK-6 | MS_arm | `σ_ult/σ_max-1` | ≥1.5 |
| KK-7 | cg_dev_mm | `Σ(m_i×x_i)/Σm_i - x_geom` | ≤5mm |
| KK-8 | s/D ratio | `wheelbase/D_rotor` | ≥1.1 |
| KK-9 | BW_Hz | `Kapalı döngü -3dB` | ≥10Hz |
| KK-11 | roll_rms_deg | `std(roll_log) @ hover` | ≤1.0° |
| KK-12 | V_max_ms | `Motor gücü + aerodinamik` | ≥req |
| KK-13 | Q_yaw_Nm | `Σ(sign_i×Q_i)` | ≤0.01 |
| KK-Perf | TW_worst | `TW×(ρ_worst/ρ_SL)` | ≥1.5 |

---
## 📋 Gereksinim Listesi (Kategori Bazlı)

### 1. İTKİ & UÇUŞ PERFORMANSI

| REQ-ID | Gereksinim | Formül (Özet) | Min | Hedef | KK |
|--------|-----------|---------------|-----|-------|----|
| `PR-IT-01` | Toplam İtki Kuvveti (Hover) | `T_total = MTOW_kg × g × TW_req` | 2×MTOW×g | 2.2×MTOW×g | KK-1 (T/W≥2.0) |
| `PR-IT-02` | Rotor Başına İtki | `T_per_rotor = T_total / n_rotors` | T_total/n | T_total/n | KK-1 |
| `PR-IT-03` | Disk Yükleme (DL) | `DL = T_per_rotor / (π × R²)` | 50 | ≤200 | KK-4 (DL≤300 N/m²) |
| `PR-IT-04` | Güç Yükleme (PL) | `PL = T_total / P_total_hover` | 6 | ≥8 | KK-5 (PL≥8 N/W) |
| `PR-IT-05` | Figure of Merit (FM) | `FM = T√(T/2ρA) / P_shaft` | 0.55 | ≥0.65 | KK-2 (FM≥0.60) |
| `PR-IT-06` | Maksimum Yatay Hız | `V_max = kullanıcı gereksinimi [WBS 1.1-3.2]` | 5 | ≥V_req | KK-12 (V_max≥req) |
| `PR-IT-07` | Tırmanma Hızı | `V_climb = kullanıcı gereksinimi [WBS 1.1-3.7]` | 1 | ≥V_climb_req | — |
| `PR-IT-08` | OEI (Tek Motor Arızası) Hover Kapasitesi | `T_OEI = (n-1)/n × T_total ≥ MTOW×g × 1.05` | MTOW×g | ≥1.05×MTOW×g | KK-1 (N+1 redundancy) |
| `PR-IT-09` | Maksimum Operasyonel İrtifa | `P_available(alt) = P_SL × (ρ_alt/ρ_SL)^0.9` | 0 | ≥alt_MSL_req | KK-4 (DL performans zarfı) |
| `PR-IT-10` | Yaw Torque Dengesi | `|ΣQ_CW - ΣQ_CCW| ≤ 0.01 N·m` | — | 0 | KK-13 (Q_yaw≤0.01 N·m) |

**Detaylar:**
- **`PR-IT-01` [PERF]** — Tüm rotorların ürettiği toplam kaldırma kuvveti. MTOW×g'nin en az 2 katı olmalıdır. Hover marjı = T_
  - Formül: `T_total = MTOW_kg × g × TW_req`
  - Standart: Raymer §17 | NDARC NASA/TM-2015-218751
- **`PR-IT-02` [PERF]** — Her bir rotordan üretilmesi gereken itki. N+1 redundancy: (n-1) rotor ile T ≥ MTOW×g sağlanmalı.
  - Formül: `T_per_rotor = T_total / n_rotors`
  - Standart: NDARC | Leishman §2
- **`PR-IT-03` [PERF]** — Düşük DL → yüksek verim (FM↑), büyük rotor; yüksek DL → kompakt ama verimsiz. Hedef: <200 N/m² optim
  - Formül: `DL = T_per_rotor / (π × R²)`
  - Standart: NDARC | Prouty Rotorcraft Aerodynamics
- **`PR-IT-04` [PERF]** — Sistemin enerji verimliliğinin ana göstergesi. Yüksek PL → daha uzun menzil ve hover süresi. Hedef: 
  - Formül: `PL = T_total / P_total_hover`
  - Standart: NDARC | Leishman Rotorcraft §2
- **`PR-IT-05` [PERF]** — Rotor verim göstergesi; ideal hovere göre gerçek verimliliği ölçer. FM=1.0 → ideal; tipik multirotor
  - Formül: `FM = T√(T/2ρA) / P_shaft`
  - Standart: Leishman §3 | UIUC Propeller DB
- **`PR-IT-06` [PERF]** — Maksimum yatay ileri uçuş hızı. Yüksek hız → daha fazla eğim açısı (tilt) ve güç gerektirir. Limit: 
  - Formül: `V_max = kullanıcı gereksinimi [WBS 1.1-3.2]`
  - Standart: EASA 2019/947 Art.5 | JARUS SORA §2.3.2
- **`PR-IT-07` [PERF]** — Dikey tırmanma performansı. T_excess = T_total - Weight → tırmanma için kullanılabilir fazla itki.
  - Formül: `V_climb = kullanıcı gereksinimi [WBS 1.1-3.7]`
  - Standart: ADS-33E-PRF Tablo 2 | PX4 MC Position
- **`PR-IT-08` [SAFE]** — N+1 redundancy: 1 motor çalışmasa da %5 güvenlik marjıyla hover. N+2 gerekiyorsa: (n-2)/n × T_total 
  - Formül: `T_OEI = (n-1)/n × T_total ≥ MTOW×g × 1.05`
  - Standart: EASA SC-VTOL §2530 | JARUS SORA OSO#14
- **`PR-IT-09` [PERF]** — İrtifa arttıkça hava yoğunluğu düşer (ρ↓) → motor gücü düşer. ISA+25°C'de de hedef irtifaya ulaşılab
  - Formül: `P_available(alt) = P_SL × (ρ_alt/ρ_SL)^0.9`
  - Standart: ICAO Doc 8168 | ISA Standard | NDARC §3.2
- **`PR-IT-10` [DES]** — CW ve CCW dönen rotorların toplam tork farkı minimize edilmeli. Büyük dengesizlik → trim yaw hatası 
  - Formül: `|ΣQ_CW - ΣQ_CCW| ≤ 0.01 N·m`
  - Standart: Mahony 2012 | Prouty §4

### 2. ENERJİ & DAYANIKLILIK

| REQ-ID | Gereksinim | Formül (Özet) | Min | Hedef | KK |
|--------|-----------|---------------|-----|-------|----|
| `PR-EN-01` | Hover Güç Tüketimi | `P_hover = T_total × v_induced = T_total × √(T_tota...` | — | hesaplanan | KK-5 (PL bağlı) |
| `PR-EN-02` | Toplam Sistem Hover Gücü | `P_total = P_hover / (FM × η_motor × η_esc)` | — | hesaplanan | KK-5 |
| `PR-EN-03` | Hover Dayanıklılık (Endurance) | `t_hover = (E_bat × η_discharge) / P_total - t_rese...` | endurance_req | ≥endurance_req × 1.2 | KK-3 (t_hover≥req×1.2) |
| `PR-EN-04` | Batarya Kapasitesi | `C_mAh = (P_total × t_hover × 1.2) / (V_nom × η_dis...` | — | hesaplanan | KK-3 |
| `PR-EN-05` | Sistem Enerji Verimliliği | `η_system = PL = T_total/P_total ≥ 8 N/W` | 6 | ≥8 | KK-5 (PL≥8 N/W) |
| `PR-EN-06` | Maksimum Menzil (İleri Uçuş) | `R_max = (E_bat × η × L/D_eff) / (MTOW × g)` | — | ≥range_req | KK-12 |
| `PR-EN-07` | Batarya Rezerv Marjı | `E_reserve = E_bat × reserve_pct/100 ≥ P_total × t_...` | 10 | ≥20 | KK-3 |
| `PR-EN-08` | Soğuk/Sıcak Hava Güç Düşümü | `P_derate(T) = P_SL × (ρ(T)/ρ_SL); ΔP_cold = 1 - (S...` | — | hesaplanan | KK-3 (en kötü durumda) |

**Detaylar:**
- **`PR-EN-01` [PERF]** — Teorik minimum hover gücü. Gerçek güç = P_hover / (FM × η_motor × η_esc). İrtifa ve sıcaklık düzeltm
  - Formül: `P_hover = T_total × v_induced = T_total × √(T_total/2ρA×n)`
  - Standart: Leishman §2 | NDARC §4
- **`PR-EN-02` [PERF]** — Motor verimliliği, ESC verimliliği ve FM dahil gerçek sistem gücü. Enerji bütçesinin temel girdisi.
  - Formül: `P_total = P_hover / (FM × η_motor × η_esc)`
  - Standart: NDARC §4 | Peukert model
- **`PR-EN-03` [PERF]** — %20 güvenlik marjı dahil. Peukert kaybı: t_Peukert = t_nominal × (I_nominal/I_hover)^(n_P-1). n_P (L
  - Formül: `t_hover = (E_bat × η_discharge) / P_total - t_reserve`
  - Standart: ASTM F3002-14a | NDARC §4
- **`PR-EN-04` [PERF]** — Gerekli batarya kapasitesi. Peukert ve %20 rezerv dahil. C-rate kontrolü: I_hover/(C_mAh/1000) ≤ C_r
  - Formül: `C_mAh = (P_total × t_hover × 1.2) / (V_nom × η_discharge) × 1000`
  - Standart: ASTM F3005-14a | IEC 62619
- **`PR-EN-05` [PERF]** — Toplam sistem güç yüklemesi. Motor + ESC + pervane birlikte optimize edilmeli.
  - Formül: `η_system = PL = T_total/P_total ≥ 8 N/W`
  - Standart: eCalc metodolojisi | NDARC
- **`PR-EN-06` [PERF]** — Breguet menzil denklemi multirotor versiyonu. Maksimum menzil için optimum hız V_opt = √(2×P_hover/D
  - Formül: `R_max = (E_bat × η × L/D_eff) / (MTOW × g)`
  - Standart: NDARC §4 | Prouty §4
- **`PR-EN-07` [SAFE]** — İniş sonrası bataryada kalması gereken minimum enerji. En az 3 dakika acil uçuş rezervi + %20 nomina
  - Formül: `E_reserve = E_bat × reserve_pct/100 ≥ P_total × t_min_land`
  - Standart: FAA AC 20-184 | EASA AMC RPAS.1309
- **`PR-EN-08` [PERF]** — Sıcak havada: motor derate. Soğuk havada: batarya kapasitesi %10-20 düşer. Her iki durumda da endura
  - Formül: `P_derate(T) = P_SL × (ρ(T)/ρ_SL); ΔP_cold = 1 - (SoH_bat(T)/SoH_SL)`
  - Standart: IEC 62619 §7 | MIL-STD-810H M501 | ISA

### 3. YAPISAL & MEKANİK

| REQ-ID | Gereksinim | Formül (Özet) | Min | Hedef | KK |
|--------|-----------|---------------|-----|-------|----|
| `PR-YP-01` | Kol Güvenlik Marjı (MS) | `MS = σ_ult/σ_max - 1; σ_max = M_DLL×c/I` | 1.2 | ≥1.5 | KK-6 (MS≥1.5) |
| `PR-YP-02` | İniş Takımı Darbe Dayanımı | `MS_leg = σ_ult/σ_impact - 1; σ_impact = F_impact×L...` | 1.2 | ≥1.5 | KK-6 |
| `PR-YP-03` | İlk Doğal Frekans (Modal) | `f_nat_1 ≥ 2 × RPM_max/60 (Hz)` | — | ≥2×RPM_max/60 | KK-6 (Campbell kriteri) |
| `PR-YP-04` | IMU Titreşim Seviyesi | `a_IMU_rms ≤ 0.3 g (tüm eksenler)` | — | ≤0.3 | KK-6 (titreşim) |
| `PR-YP-05` | CG Sapması (Ağırlık Merkezi) | `|CG - geometrik_merkez| ≤ 5 mm (tüm eksenler)` | — | ≤5 | KK-7 (CG≤5mm) |
| `PR-YP-06` | Motor Montaj Titreşim İletim Oranı | `TR = k_mount/(k_mount - m_motor×ω²) ≤ 0.15` | — | ≤0.15 | KK-6 (motor mount TR) |
| `PR-YP-07` | Rotor Aralık Oranı (s/D) | `s/D = wheelbase / D_rotor ≥ 1.1 (komşu rotor merke...` | 1.05 | ≥1.1 | KK-8 (s/D≥1.1) |
| `PR-YP-08` | Pervane Uç Zemini Aralığı (Tip Clearance) | `tip_clearance = landing_gear_height - rotor_z_pos ...` | 0.03 | ≥0.05 | — |

**Detaylar:**
- **`PR-YP-01` [SAFE]** — Tasarım limit yükü (DLL) = 3.5g. Malzeme: CFRP σ_ult≈600 MPa, Al 6061 σ_ult≈310 MPa.
  - Formül: `MS = σ_ult/σ_max - 1; σ_max = M_DLL×c/I`
  - Standart: MIL-HDBK-5J | EASA SC-VTOL §2301 | ASTM D3039
- **`PR-YP-02` [SAFE]** — 1.5g dikey darbe yükü altında iniş takımı bütünlüğü. Enerji absorpsiyonu: E = 0.5×MTOW×v_land², v_la
  - Formül: `MS_leg = σ_ult/σ_impact - 1; σ_impact = F_impact×L_leg/I_leg×c`
  - Standart: FAR/CS 23.473 | EASA SC-VTOL §2520 | MIL-HDBK-5J
- **`PR-YP-03` [DES]** — İlk modal frekans, maksimum RPM'in 2 katından büyük olmalı. Campbell diyagramında rezonans marjı ≥ %
  - Formül: `f_nat_1 ≥ 2 × RPM_max/60 (Hz)`
  - Standart: ISO 10816-3 | Campbell diyagramı | Rao Vibrations
- **`PR-YP-04` [DES]** — Yüksek titreşim → EKF drift, motor health yanlış okuma. Anti-vibration mount ile ≤0.3 g RMS hedeflen
  - Formül: `a_IMU_rms ≤ 0.3 g (tüm eksenler)`
  - Standart: PX4 Vibration Guide | ISO 10816
- **`PR-YP-05` [DES]** — Tüm 3 eksende CG geometrik merkezden sapması. CG zarfı: boş/dolu/yakıtsız tüm konfigürasyonlar için 
  - Formül: `|CG - geometrik_merkez| ≤ 5 mm (tüm eksenler)`
  - Standart: EASA SC-VTOL §2510 | Raymer §6
- **`PR-YP-06` [DES]** — Motor montaj yay rijitliği tasarımı. TR<0.15 → gövdeye iletilen titreşim %15'ten az.
  - Formül: `TR = k_mount/(k_mount - m_motor×ω²) ≤ 0.15`
  - Standart: Rao Mechanical Vibrations §4 | ISO 10816
- **`PR-YP-07` [DES]** — Rotor-rotor aerodinamik etkileşimi azaltmak için minimum aralık. s/D<1.1 → verim kaybı >%8.
  - Formül: `s/D = wheelbase / D_rotor ≥ 1.1 (komşu rotor merkez-merkez / çap)`
  - Standart: Leishman §5 | Lerche 2015 | AHS Forum
- **`PR-YP-08` [DES]** — Zemindeyken pervane ile zemin arasındaki minimum mesafe. Kalkış/iniş güvenliği için kritik.
  - Formül: `tip_clearance = landing_gear_height - rotor_z_pos - R ≥ 0.05 m`
  - Standart: FAR/CS 23.473 | EASA SC-VTOL §2520

### 4. KONTROL & KARARLILIK

| REQ-ID | Gereksinim | Formül (Özet) | Min | Hedef | KK |
|--------|-----------|---------------|-----|-------|----|
| `PR-KK-01` | Kontrol Bant Genişliği (Attitude BW) | `BW_attitude ≥ 10 Hz (kapalı döngü -3dB noktası)` | 5 | ≥10 | KK-9 (BW≥10 Hz) |
| `PR-KK-02` | Faz Marjı (PM) | `PM ≥ 45° (Bode diyagramı, açık döngü)` | 30 | ≥45 | KK-9 |
| `PR-KK-03` | Kazanç Marjı (GM) | `GM ≥ 6 dB (Bode diyagramı)` | 3 | ≥6 | KK-9 |
| `PR-KK-04` | Hover Roll/Pitch RMS (SITL) | `roll_rms ≤ 1.0°, pitch_rms ≤ 1.0° @ sakin hava hov...` | — | ≤1.0 | KK-11 (SITL≤1.0°) |
| `PR-KK-05` | Yükseklik Tutma Doğruluğu | `alt_rms ≤ 0.1 m (indoor), ≤ 0.2 m (outdoor GPS)` | — | ≤0.1 (indoor) | KK-11 |
| `PR-KK-06` | Konumlama Doğruluğu (Hover) | `pos_rms ≤ 0.5 m (GPS+EKF) | ≤ 0.02 m (RTK)` | — | ≤pos_acc_req | KK-11 |
| `PR-KK-07` | Yaw Drift (Yaw Kararlılığı) | `yaw_rms ≤ 2.0° @ hover (GPS heading)` | — | ≤2.0 | KK-11 |
| `PR-KK-08` | Rüzgar Gustu Konum Sapması | `pos_dev_gust ≤ 2.0 m (5 m/s@45° gust sonrası)` | — | ≤2.0 | KK-11 (gust testi) |
| `PR-KK-09` | Dual IMU Failover Gecikmesi | `t_failover ≤ 100 ms (birincil → ikincil IMU geçiş)` | — | ≤100 | KK-9 (dual IMU) |
| `PR-KK-10` | Anti-Windup Saturasyon Sınırı | `RPM_cmd ∈ [RPM_min, RPM_max]; integrator ∈ [-I_lim...` | RPM_min=1500 | optimal | KK-9 |

**Detaylar:**
- **`PR-KK-01` [PERF]** — Roll/pitch attitude kontrolünün yanıt bant genişliği. Yüksek BW → hızlı tepki; ancak sensör gürültüs
  - Formül: `BW_attitude ≥ 10 Hz (kapalı döngü -3dB noktası)`
  - Standart: MIL-F-9490D | ADS-33E-PRF Tablo 2
- **`PR-KK-02` [DES]** — Kapalı döngü kararlılık marjı. PM<30° → aşımlar ve salınımlar. Hedef: 45-60° robustluk için yeterli.
  - Formül: `PM ≥ 45° (Bode diyagramı, açık döngü)`
  - Standart: MIL-F-9490D §3.4.1 | Control Systems Theory
- **`PR-KK-03` [DES]** — Sistem parametresi değişimlerine karşı kazanç robustluğu. GM<6dB → parametre varyasyonunda kararsızl
  - Formül: `GM ≥ 6 dB (Bode diyagramı)`
  - Standart: MIL-F-9490D §3.4.2 | ADS-33E-PRF
- **`PR-KK-04` [PERF]** — SITL simülasyonda ölçülen açısal kararlılık. Gerçek uçuşta <2° beklenir. Rüzgarsız nominal hover tes
  - Formül: `roll_rms ≤ 1.0°, pitch_rms ≤ 1.0° @ sakin hava hover`
  - Standart: PX4 QA Standard | DO-178C
- **`PR-KK-05` [PERF]** — Barometrik/lidar/optical flow sensör füzyonu ile yükseklik tutma. Indoor: lidar + optical flow; Outd
  - Formül: `alt_rms ≤ 0.1 m (indoor), ≤ 0.2 m (outdoor GPS)`
  - Standart: PX4 MC Position Control | Mahony 2012
- **`PR-KK-06` [PERF]** — Statik hover noktasından sapma. GPS: ±0.5 m; SBAS: ±0.2 m; RTK: ±0.02 m. Kullanıcı gereksinimi [WBS 
  - Formül: `pos_rms ≤ 0.5 m (GPS+EKF) | ≤ 0.02 m (RTK)`
  - Standart: RTCA DO-316A | EUROCAE ED-127 | FAA AC 20-138D
- **`PR-KK-07` [PERF]** — Compass ve EKF kaynaklı yaw drift. Manyetometre kalibrasyonu ve compass-mot kompanzasyonu kritik.
  - Formül: `yaw_rms ≤ 2.0° @ hover (GPS heading)`
  - Standart: PX4 QA | ADS-33E-PRF §3.3.5
- **`PR-KK-08` [PERF]** — 5 m/s 45° güst baskısında maksimum konum sapması. Toparlanma süresi ≤5 saniye ayrıca kontrol edilir.
  - Formül: `pos_dev_gust ≤ 2.0 m (5 m/s@45° gust sonrası)`
  - Standart: MIL-SPEC-8785C | Dryden PSD | EASA CS-23
- **`PR-KK-09` [SAFE]** — IMU tutarsızlığı tespitinden failover tamamlanmasına kadar geçen süre. 100 ms aşılırsa uçuş kararsız
  - Formül: `t_failover ≤ 100 ms (birincil → ikincil IMU geçiş)`
  - Standart: DO-178C Level C | ARP4754A | EASA SC-VTOL §2570
- **`PR-KK-10` [DES]** — Integratör sarma önleme. Saturasyon aralığı dışında back-calculation. Öncelik: yükseklik > yaw > rol
  - Formül: `RPM_cmd ∈ [RPM_min, RPM_max]; integrator ∈ [-I_lim, +I_lim]`
  - Standart: Johansen & Fossen 2013 | PX4 MC Rate Control

### 5. AERODİNAMİK

| REQ-ID | Gereksinim | Formül (Özet) | Min | Hedef | KK |
|--------|-----------|---------------|-----|-------|----|
| `PR-AD-01` | Rotor-Rotor Etkileşim Verimi Kaybı | `Δη_interaction = 1 - η_int = 0.15×exp(-3.5×(s/D-1)...` | — | ≤5 | KK-8 (etkileşim) |
| `PR-AD-02` | İleri Uçuş Tilt Açısı | `θ_tilt = atan(D_parasite / (MTOW×g)) ≤ 30°` | — | ≤20 (nominal) | — |
| `PR-AD-03` | Pervane Uç Hızı (Mach) | `M_tip = V_tip/a ≤ 0.70` | — | ≤0.65 | — |
| `PR-AD-04` | Gürültü Seviyesi (OASPL) | `OASPL ≤ 70 dBA @ 1 m (hovering, ISO 3744)` | — | ≤65 (şehir içi) | — |
| `PR-AD-05` | Ground Effect Katkısı | `T_IGE/T_OGE = 1/(1-(D/4z)²) ≥ 1.05 (z/D < 0.5)` | 1.0 | ≥1.05 (z/D<0.5) | — |

**Detaylar:**
- **`PR-AD-01` [PERF]** — Bitişik rotorların aerodinamik etkileşim kaybı. s/D=1.1 → %8 kayıp; s/D=1.5 → %2 kayıp. Hedef: ≤%5 (
  - Formül: `Δη_interaction = 1 - η_int = 0.15×exp(-3.5×(s/D-1)) ≤ 8%`
  - Standart: Leishman §5 | Lerche 2015 | AHS Forum 2019
- **`PR-AD-02` [PERF]** — İleri uçuşta çerçevenin öne eğim açısı. 30°'yi aşarsa gövde direnci dramatik artar.
  - Formül: `θ_tilt = atan(D_parasite / (MTOW×g)) ≤ 30°`
  - Standart: Prouty §4 | Bramwell Helicopter Dynamics
- **`PR-AD-03` [DES]** — Uç Mach sayısı 0.7'yi aşarsa kompresibilite etkisi ve gürültü dramatik artar. Büyük çaplı yavaş döne
  - Formül: `M_tip = V_tip/a ≤ 0.70`
  - Standart: Leishman §3 | NeuralFoil kompresibilite limit
- **`PR-AD-04` [FUNC]** — Şehir içi operasyon için akustik gereksinim. Düşük RPM + büyük çap → daha sessiz.
  - Formül: `OASPL ≤ 70 dBA @ 1 m (hovering, ISO 3744)`
  - Standart: ISO 3744:2010 | EASA UAS Noise Std. | FW-H model
- **`PR-AD-05` [PERF]** — Yer etkisiyle kalkışta fazladan %5+ itki kazanımı. Kalkış güç bütçesinde ve hover ceiling hesabında 
  - Formül: `T_IGE/T_OGE = 1/(1-(D/4z)²) ≥ 1.05 (z/D < 0.5)`
  - Standart: Cheeseman & Bennett 1955 | Leishman §7

### 6. AĞIRLIK & KÜTLE BÜTÇESİ

| REQ-ID | Gereksinim | Formül (Özet) | Min | Hedef | KK |
|--------|-----------|---------------|-----|-------|----|
| `PR-AG-01` | Payload Kütlesi Fraksiyonu | `f_payload = m_payload / MTOW ≥ 0.15` | 0.10 | ≥0.15 | — |
| `PR-AG-02` | Yapı Kütlesi Fraksiyonu | `f_struct = m_frame / MTOW ≈ 0.25-0.35 (CFRP: 0.22-...` | 0.20 | 0.25-0.30 | — |
| `PR-AG-03` | Tahrik Sistemi Kütlesi Fraksiyonu | `f_prop = (m_motors + m_esc + m_prop×n) / MTOW ≈ 0....` | 0.10 | 0.12-0.18 | — |
| `PR-AG-04` | Batarya Kütlesi Fraksiyonu | `f_bat = m_battery / MTOW ≈ 0.25-0.40` | 0.20 | 0.25-0.35 | — |
| `PR-AG-05` | Aviyonik & Kablo Kütlesi | `m_avionics = m_FC + m_GPS + m_IMU + m_ESC_board + ...` | — | hesaplanan | — |
| `PR-AG-06` | Kütle Bütçesi Kapanışı | `|Σm_bileşen - MTOW| / MTOW ≤ 1%` | — | ≤1 | — |

**Detaylar:**
- **`PR-AG-01` [DES]** — Payload fraksiyonu tasarımın etkinliğini gösterir. f_payload<0.10 → overdesigned veya payload çok ha
  - Formül: `f_payload = m_payload / MTOW ≥ 0.15`
  - Standart: Staufenbiel Methodik | NDARC | Raymer §15
- **`PR-AG-02` [DES]** — Yapısal kütlenin MTOW'a oranı. CFRP: 0.22-0.28; Al: 0.28-0.35; plastik: 0.30-0.40.
  - Formül: `f_struct = m_frame / MTOW ≈ 0.25-0.35 (CFRP: 0.22-0.28)`
  - Standart: Staufenbiel | Raymer §15 Tablo 15.2
- **`PR-AG-03` [DES]** — Motor + ESC + pervane toplam kütlesi. Yüksek güç gereksinimi → f_prop artar.
  - Formül: `f_prop = (m_motors + m_esc + m_prop×n) / MTOW ≈ 0.12-0.20`
  - Standart: NDARC | eCalc benchmarking
- **`PR-AG-04` [DES]** — Batarya kütlesi MTOW'un önemli bölümünü oluşturur. Li-Ion → daha düşük f_bat; LiPo → orta; yakıt pil
  - Formül: `f_bat = m_battery / MTOW ≈ 0.25-0.40`
  - Standart: Staufenbiel | NDARC §5 | Quan §3
- **`PR-AG-05` [DES]** — Kablo ağırlığı genellikle göz ardı edilir ama kritik: m_cables ≈ 0.02-0.04 × MTOW (m_misc dahil).
  - Formül: `m_avionics = m_FC + m_GPS + m_IMU + m_ESC_board + m_cables`
  - Standart: Raymer §15 | Dahili BOM [WBS 12.1]
- **`PR-AG-06` [DES]** — Tüm bileşenler toplandığında MTOW hedefine uyum. Kapanış hatası >5% → tasarım revizyonu gerekli.
  - Formül: `|Σm_bileşen - MTOW| / MTOW ≤ 1%`
  - Standart: INCOSE SE Handbook v4 §7 | Raymer §15

### 7. GÜVENLİK & REDUNDANCY

| REQ-ID | Gereksinim | Formül (Özet) | Min | Hedef | KK |
|--------|-----------|---------------|-----|-------|----|
| `PR-GV-01` | Katastrofik Arıza Olasılığı | `P(katastrofik) ≤ 10⁻⁷ / uçuş saati (FTA)` | — | ≤1e-7 | — |
| `PR-GV-02` | OEI Hover Süresi | `t_OEI_hover ≥ 30 saniye (kontrollü iniş için yeter...` | 15 | ≥30 | KK-1 (OEI) |
| `PR-GV-03` | RC Link Kayıp Süresi → RTL Başlatma | `t_RTL_trigger ≤ 3 saniye (RC link kaybından itibar...` | 1 | ≤3 | — |
| `PR-GV-04` | Geofence İhlali Tepki Süresi | `t_fence_action ≤ 1 saniye (ihlal tespitinden önlem...` | — | ≤1 | — |
| `PR-GV-05` | Yazılım DAL Seviyesi | `DAL seviyesi ≥ SAIL seviyesinden türetilen minimum...` | DAL-D | SAIL'e göre | — |
| `PR-GV-06` | MISRA-C Kritik İhlal | `MISRA_critical_violations = 0` | — | 0 | — |
| `PR-GV-07` | Batarya Termal Kesim Sıcaklığı | `T_cutoff = T_max_cell - 5°C (acil güç kesimi)` | T_max-15 | T_max-10 | — |

**Detaylar:**
- **`PR-GV-01` [SAFE]** — Toplam güvenlik hedefi. FTA (Hata Ağacı) ile doğrulanır. SAIL-III → 1e-6/h; SAIL-IV → 1e-7/h.
  - Formül: `P(katastrofik) ≤ 10⁻⁷ / uçuş saati (FTA)`
  - Standart: ARP4761A | JARUS SORA OSO tablosu | ED-135
- **`PR-GV-02` [SAFE]** — Tek motor arızasında güvenli iniş için yeterli hover süresi. Bu sürede RTL komutu verilmeli veya oto
  - Formül: `t_OEI_hover ≥ 30 saniye (kontrollü iniş için yeterli)`
  - Standart: EASA SC-VTOL §2530 | JARUS SORA OSO#14
- **`PR-GV-03` [SAFE]** — RC bağlantısı kesildiğinde otomatik RTL başlatma süresi. BVLOS → heartbeat timeout ≤ 5 s.
  - Formül: `t_RTL_trigger ≤ 3 saniye (RC link kaybından itibaren)`
  - Standart: EASA AMC RPAS.1309 | JARUS SORA OSO#06
- **`PR-GV-04` [SAFE]** — Geofence sınırı aşıldığında otomatik aksiyon (RTL/LAND/hover) süresi.
  - Formül: `t_fence_action ≤ 1 saniye (ihlal tespitinden önlem alımına)`
  - Standart: EASA AMC RPAS.1309 | DO-365 | JARUS SORA OSO#05
- **`PR-GV-05` [SAFE]** — SAIL-I/II → DAL-D; SAIL-III → DAL-C; SAIL-IV → DAL-B; Certified → DAL-A. MC/DC kapsama DAL-C'den iti
  - Formül: `DAL seviyesi ≥ SAIL seviyesinden türetilen minimum seviye`
  - Standart: DO-178C | ARP4754A | EASA SC-VTOL §2580
- **`PR-GV-06` [SAFE]** — Yazılım güvenliği için MISRA-C kritik kurallar ihlal edilemez. Advisory ihlaller ≤10 ile sınırlı tut
  - Formül: `MISRA_critical_violations = 0`
  - Standart: MISRA-C:2012 | DO-178C §6 | AUTOSAR C++14
- **`PR-GV-07` [SAFE]** — Termal kaçak riskini önlemek için otomatik güç kesimi. WARN @ T_max-15°C; LIMIT @ T_max-5°C; CUTOFF 
  - Formül: `T_cutoff = T_max_cell - 5°C (acil güç kesimi)`
  - Standart: IEC 62619 §7 | UN 38.3 §38.3.4 | RTCA DO-311A

### 8. ÇEVRE & DAYANIM

| REQ-ID | Gereksinim | Formül (Özet) | Min | Hedef | KK |
|--------|-----------|---------------|-----|-------|----|
| `PR-CD-01` | Operasyonel Sıcaklık Aralığı | `T_ops_min ≤ T_component_min; T_ops_max ≥ T_compone...` | -20 / +55 | -10 / +50 | — |
| `PR-CD-02` | IP Koruma Sınıfı Doğrulaması | `IP_class ≥ IP43 (min); IP54 (yağmurlu); IP65 (su ü...` | IP43 | IP_class_req | — |
| `PR-CD-03` | DO-160G Titreşim Testi Geçer | `Tüm bileşenler DO-160G §8 Kategori B/C testini geç...` | — | PASS | — |
| `PR-CD-04` | GPS Anti-Spoofing Performansı | `GPS_SNR ≥ 35 dB; compass_residual ≤ 3 mGauss` | — | ≥35 dB / ≤3 mGauss | — |
| `PR-CD-05` | IATA Taşıma Uyumluluğu | `Wh > 100 → UN 3480/3481 belgesi; Wh > 300 → Sınıf ...` | — | uyumlu | — |

**Detaylar:**
- **`PR-CD-01` [DES]** — Tüm bileşenlerin (motor, ESC, batarya, FC) sıcaklık aralıkları operasyon sıcaklığını karşılamalı.
  - Formül: `T_ops_min ≤ T_component_min; T_ops_max ≥ T_component_max`
  - Standart: DO-160G §4 | MIL-STD-810H Method 501/502 | IEC 62619
- **`PR-CD-02` [DES]** — Toz (ilk rakam) ve su (ikinci rakam) koruması. IP54: toz koruma + her yönden su sıçraması. IP65: tam
  - Formül: `IP_class ≥ IP43 (min); IP54 (yağmurlu); IP65 (su üstü)`
  - Standart: IEC 60529 | MIL-STD-810H Method 506 | DO-160G §14
- **`PR-CD-03` [DES]** — 5-2000 Hz random vibrasyon testi. Kategori B: genel havacılık; Kategori C: rotor wing yakını.
  - Formül: `Tüm bileşenler DO-160G §8 Kategori B/C testini geçmeli`
  - Standart: DO-160G §8 | MIL-STD-810H Method 514
- **`PR-CD-04` [DES]** — EMI/EMC etkisi altında GPS güvenilirliği. Motor akımı → manyetometre müdahalesi; compass-mot kompanz
  - Formül: `GPS_SNR ≥ 35 dB; compass_residual ≤ 3 mGauss`
  - Standart: RTCA DO-316A | PX4 Compass Mot Cal | EUROCAE ED-269
- **`PR-CD-05` [DES]** — Batarya ile hava taşımacılığı gereksinimleri. E_Wh > 100 Wh → IATA Class 9 tehlikeli madde sınıfland
  - Formül: `Wh > 100 → UN 3480/3481 belgesi; Wh > 300 → Sınıf 9 PI 968/969`
  - Standart: IATA DGR 65th Ed. | UN 38.3 | ICAO Doc 9284

### 9. HABERLEŞme & SİSTEM ENTEGRASYONU

| REQ-ID | Gereksinim | Formül (Özet) | Min | Hedef | KK |
|--------|-----------|---------------|-----|-------|----|
| `PR-HB-01` | RC Link Gecikme Süresi | `t_latency_RC ≤ 30 ms (transmitter → FC output)` | — | ≤20 | — |
| `PR-HB-02` | C2 Datalink Kullanılabilirlik | `C2_availability ≥ 99.9% (BVLOS zorunlu)` | 99.0 | ≥99.9 | — |
| `PR-HB-03` | C2 Datalink Gecikme Süresi | `t_latency_C2 ≤ 200 ms (BVLOS komuta döngüsü)` | — | ≤100 | — |
| `PR-HB-04` | Remote ID Yayın Uyumu | `ASTM F3411-22a → 1 Hz yayın; menzil ≥ 300 m` | — | PASS | — |
| `PR-HB-05` | UTM Uçuş Planı Onayı | `flight_plan_approved = True (BVLOS ve SAIL-III+ iç...` | — | True (koşullu) | — |
| `PR-HB-06` | Sensör Kalibrasyon Doğruluğu | `IMU Allan deviation ≤ 0.1°/√h; Mag residual ≤ 20 m...` | — | ≤0.1/≤20 | — |
| `PR-HB-07` | CI/CD Build Pipeline Başarı | `Tüm CI aşamaları PASS; coverage ≥ 80%; MISRA criti...` | — | PASS / ≥80% / =0 | — |
| `PR-HB-08` | SITL Regresyon Test Geçer | `4 SITL testi PASS: hover, mission, gust, OEI` | — | 4/4 PASS | — |
| `PR-HB-09` | Performans Zarfı En Kötü Durum T/W | `TW_worst = TW_matrix.min() ≥ 1.5 (max alt + ISA+35...` | 1.2 | ≥1.5 | — |

**Detaylar:**
- **`PR-HB-01` [FUNC]** — Pilot komutunun motor çıkışına ulaşma süresi. 30 ms üstü → pilot feedback gecikmesi hissedilir.
  - Formül: `t_latency_RC ≤ 30 ms (transmitter → FC output)`
  - Standart: ETSI EN 300 328 | DO-160G §20 | FCC Part 15
- **`PR-HB-02` [FUNC]** — BVLOS operasyonlarda komuta-kontrol linkinin kullanılabilirlik oranı. LTE primer + 915 MHz yedek → r
  - Formül: `C2_availability ≥ 99.9% (BVLOS zorunlu)`
  - Standart: JARUS SORA OSO#10 | EUROCAE ED-269 | DO-365
- **`PR-HB-03` [FUNC]** — GCS'den FC'ye komut ulaşma süresi. >200 ms → BVLOS güvenli olmayan tepki süresi.
  - Formül: `t_latency_C2 ≤ 200 ms (BVLOS komuta döngüsü)`
  - Standart: JARUS SORA OSO#10 | EUROCAE ED-269
- **`PR-HB-04` [FUNC]** — Kimlik, konum, irtifa, hız ve operatör konumu 802.11/BT5 ile yayınlanmalı. EASA → tüm kategorilerde 
  - Formül: `ASTM F3411-22a → 1 Hz yayın; menzil ≥ 300 m`
  - Standart: ASTM F3411-22a | EASA (EU) 2022/425 | FAA 14 CFR §89
- **`PR-HB-05` [FUNC]** — USS (UAS Service Supplier) aracılığıyla uçuş planı onayı. BVLOS ve Specific kategori → zorunlu. VLOS
  - Formül: `flight_plan_approved = True (BVLOS ve SAIL-III+ için)`
  - Standart: ASTM F3411-22a | EASA IR 2021/664 | ICAO RPAS
- **`PR-HB-06` [FUNC]** — 6-pozisyon IMU kalibrasyonu ve manyetometre elipsoid fit. Kötü kalibrasyon → EKF drift ve attitude h
  - Formül: `IMU Allan deviation ≤ 0.1°/√h; Mag residual ≤ 20 mGauss`
  - Standart: PX4 Sensor Calibration | DO-160G §19 | IEEE 1554
- **`PR-HB-07` [FUNC]** — Her commit sonrası otomatik: lint → test → coverage → SITL regresyon. PR merge: tüm aşamalar PASS zo
  - Formül: `Tüm CI aşamaları PASS; coverage ≥ 80%; MISRA critical = 0`
  - Standart: DO-178C §6 | IEEE 829 | ISO/IEC 29119
- **`PR-HB-08` [FUNC]** — Her build'de 4 otomatik SITL testi: (1) hover_30s, (2) mission_10wpt, (3) gust_5ms, (4) OEI_landing.
  - Formül: `4 SITL testi PASS: hover, mission, gust, OEI`
  - Standart: DO-178C §6.4 | IEEE 829-2008 | PX4 MAVSDK Test
- **`PR-HB-09` [PERF]** — En yüksek irtifa ve en yüksek sıcaklıkta minimum T/W. Bu değer <1.5 ise rotor çapı büyütülmeli veya 
  - Formül: `TW_worst = TW_matrix.min() ≥ 1.5 (max alt + ISA+35°C)`
  - Standart: ICAO Doc 8168 PANS-OPS | NDARC §3 | ISA Std.

---
## 🐍 Hızlı Hesaplama Referansı

```python
# mission_profile.json → requirements.json (özet)
T_total = MTOW * g * TW_req       # PR-IT-01
DL = T_per_rotor / (pi * R²)      # PR-IT-03: ≤ 300 N/m²
PL = T_total / P_total             # PR-EN-05: ≥ 8 N/W
FM = T√(T/2ρA) / P_shaft          # PR-IT-05: ≥ 0.60
MS = σ_ult / σ_max - 1             # PR-YP-01: ≥ 1.5
t_hover = (E_bat/P_total)*60*(1-reserve) # PR-EN-03: ≥ end*1.2
rho_worst = isa_density(alt_MSL, 35)  # ISA+35°C worst case
TW_worst = TW * (rho_worst/rho_SL)   # ≥ 1.5 zorunlu
```

---
*WBS 1.2 PRD Detay Rehberi v4.0 — Nisan 2026 | 68 Gereksinim | 9 Kategori*