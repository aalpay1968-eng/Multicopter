---
name: tandem-wing-multicopter-design
description: >
  Kapsamlı Detay Tasarım (Critical Design) skill'i: Tandem Wing + MultiCopter konfigürasyonundaki
  hava araçlarının (özellikle 500 kg+ faydalı yük taşıyan yangın söndürme/kurtarma İHA'ları)
  sistematik mühendislik tasarımını yapar. MBSE yaklaşımıyla sistem gereksinimlerinden başlayarak
  aerodinamik analiz, yapısal tasarım, güç sistemi seçimi (tam elektrikli veya hibrit), FEA simülasyonu,
  termal analiz ve uyumluluk değerlendirmesine kadar tüm Critical Design Review (CDR) sürecini yönetir.
  Tasarım çıktısını profesyonel .docx raporu olarak üretir.

  MUTLAKA KULLAN: Kullanıcı "tandem wing", "multicopter tasarım", "İHA detay tasarım", "CDR", "critical design",
  "yangın söndürme İHA", "hibrit güç sistemi İHA", "500kg payload drone", "elektrikli İHA tasarım raporu",
  veya "hava aracı tasarım .docx" gibi ifadeler kullandığında bu skill'i devreye al.
  Ayrıca hava aracı konfigürasyon analizi, rotor boyutlandırma, batarya/jeneratör seçimi,
  EASA/SHGM regülasyon uyumluluğu veya uçuş performansı hesaplama görevlerinde de kullan.
---

# Tandem Wing + MultiCopter Kritik Tasarım Skill'i

## Görev Tanımı

Bu skill, 500 kg faydalı yük kapasiteli Tandem Wing + MultiCopter konfigürasyonlu hava araçlarının
**Detay Tasarımını (Critical Design Review - CDR)** gerçekleştirir. İki opsiyon üretir:
- **Opsiyon 1:** Tam Elektrikli (Fully Electric)
- **Opsiyon 2:** Hibrit Güç Sistemi (Hybrid – ICE/Turbine + Electric)

Çıktı: Profesyonel **`.docx` formatında** tasarım raporu (4 bölüm, Türkçe/İngilizce seçilebilir).

---

## Adım 1 – Sistem Gereksinimlerini Tanımla

Kullanıcıdan eksik veriler varsa sormadan önce şu **varsayılan değerleri** kullan:

| Parametre | Varsayılan Değer |
|-----------|-----------------|
| Faydalı Yük (Payload) | 500 kg |
| Görev Türü | Yangın Söndürme (su/köpük bombası) |
| İstenilen Uçuş Süresi | ≥ 20 dakika (tam yüklü) |
| Operasyonel Yükseklik | Deniz seviyesi – 3000 m MSL |
| Max. Seyir Hızı | ≥ 80 km/h (yatay uçuş) |
| Min. Askıda Kalma Süresi | ≥ 10 dakika |
| Regülasyon Çerçevesi | EASA SORA / SHGM |
| Hedef SAIL Seviyesi | SAIL IV (yüksek risk, kalabalık olmayan bölge) |

**Konfigürasyon Kararı:**
- **Tandem Wing:** Ön ve arka kanat (eş boyut veya arka kanat %15 daha büyük) – hem VTOL hem de yatay uçuş aşamasında aerodinamik verimlilik sağlar.
- **MultiCopter Rotorları:** 6–8 rotor (hexacopter/octocopter), redundancy için.

---

## Adım 2 – Ön Boyutlandırma (Preliminary Sizing)

### 2.1 Ağırlık Bütçesi (MTOW Tahmini)

```
Payload (m_payload)    = 500 kg (sabit)
Yapısal Ağırlık        ≈ 0.25 × MTOW
Güç Sistemi Ağırlığı   ≈ 0.35 × MTOW  (elektrikli)
                       ≈ 0.28 × MTOW  (hibrit)
Aviyonik + Diğer       ≈ 0.05 × MTOW

Elektrikli:  MTOW ≈ 500 / (1 - 0.25 - 0.35 - 0.05) ≈ 1429 kg → 1400-1500 kg
Hibrit:      MTOW ≈ 500 / (1 - 0.25 - 0.28 - 0.05) ≈ 1190 kg → 1100-1250 kg
```

### 2.2 Rotor Sistemi Boyutlandırması

**İtme Gereksinimi:**
```
T_total = MTOW × g × 1.3  (güvenlik faktörü)
Elektrikli: T = 1450 × 9.81 × 1.3 ≈ 18,500 N
Hibrit:     T = 1200 × 9.81 × 1.3 ≈ 15,300 N

Her rotordan gereken itme (8 rotor için):
Elektrikli: T_rotor ≈ 2,315 N/rotor
Hibrit:     T_rotor ≈ 1,915 N/rotor
```

**Rotor Çap Tahmini (Disk Yükleme):**
```
Disk Loading (DL) hedefi: 250-400 N/m²  (ağır yük İHA'lar için)
A_disk = T_rotor / DL
D_rotor ≈ 2 × √(A_disk / π)

Elektrikli: D ≈ 1.8–2.2 m (her rotor)
Hibrit:     D ≈ 1.6–2.0 m (her rotor)
```

### 2.3 Güç Sistemi Boyutlandırması

**Elektrikli Opsiyon:**
```
Hover güç tüketimi per rotor:
P_hover = T^(3/2) / (√(2ρA)) × (1/η_motor × 1/η_ESC)
η_sistem ≈ 0.75

Toplam hover gücü: ~180-220 kW
Batarya kapasitesi (30 dk için): 
E = P × t / η = 200 kW × 0.5h / 0.9 ≈ 111 kWh
Batarya kütlesi (LiPo/LiFePO4 @ 200-250 Wh/kg): ~450-550 kg
→ Enerji yoğunluğu kritik sınır! Solid-state veya Li-S değerlendirmesi gerekir.
```

**Hibrit Opsiyon:**
```
ICE/Turbine jeneratör: 150-200 kW sürekli güç
Batarya tampon: 20-30 kWh (peak demand için)
Yakıt tüketimi: ~40-60 L/saat (Jet-A veya Diesel)
Yakıt tankı: ~60 L → ~50 kg
Hibrit sistemin avantajı: Yakıt enerjisi yoğunluğu ~12,000 Wh/kg >> Batarya
```

---

## Adım 3 – Aerodinamik Analiz

### 3.1 Kanat Geometrisi (Tandem Wing)

```
Aspect Ratio hedefi: AR = 6–8 (kompakt VTOL için)
Kanat Yükü: W/S = 80-120 kg/m²

Ön kanat alanı:  S_front ≈ 4–6 m²
Arka kanat alanı: S_rear ≈ S_front × 1.15 (arka > ön)
Toplam kanat alanı: ~10-14 m²

Kanat profili: NACA 4412 veya Clark-Y (yüksek kaldırma/sürükleme oranı)
Açıklık (Span): ~4–5 m (her kanat)
Konik Oran (Taper Ratio): 0.5–0.7
```

### 3.2 Uçuş Performansı

| Parametre | Elektrikli | Hibrit |
|-----------|-----------|--------|
| Best Glide Ratio (L/D) | ~8-10 | ~8-10 |
| Stall Hızı (deniz sev.) | ~55-65 km/h | ~50-60 km/h |
| Cruise Hızı | ~80-100 km/h | ~80-120 km/h |
| Max. Menzil | ~30-50 km | ~150-300 km |
| Hover Dayanıklılığı | ~15-25 dk | ~60-120 dk |

### 3.3 VTOL → Yatay Uçuş Geçiş Analizi

Tandem Wing + MultiCopter geçiş protokolü:
1. **VTOL Fazı (0-50 m):** Tüm rotorlar aktif, kanatlar pasif
2. **Geçiş Fazı (50-150 m, 40-80 km/h):** Kanat kaldırması devreye girer, rotor gücü azalır
3. **Cruise Fazı (>150 m, >80 km/h):** Kanat kaldırması MTOW'un %40-60'ını taşır; arka rotorlar itici olarak çalışır

---

## Adım 4 – Yapısal Tasarım

### 4.1 Malzeme Seçimi

| Bileşen | Birincil Malzeme | Alternatif | Ağırlık Hedefi |
|---------|-----------------|------------|----------------|
| Ana Gövde (Fuselage) | CFRP (T700) Sandwich | Al 7075-T6 | 60-80 kg |
| Kanat Strüktürü | CFRP Monocoque | GFRP + Al spar | 30-50 kg (kanat başına) |
| Motor Kolları (Arms) | CFRP Tüp (Ø80-120mm) | Al 6061-T6 | 8-15 kg (kol başına) |
| İniş Takımı | Al 7075 + Damper | CFRP | 20-30 kg |
| Payload Bölmesi | Al 6061 / CFRP | Komposit Sandwich | 15-25 kg |

### 4.2 Yapısal Yük Senaryoları (FEA için)

**Kritik Yük Durumları:**
1. **Limit Load (LL):** 2.5g manevra + 1.5g iniş darbesi
2. **Ultimate Load (UL):** LL × 1.5 (güvenlik faktörü)
3. **Fatigue:** 1000 uçuş çevrimi, ±1g dinamik yükleme
4. **Torque (Motor Arıza):** Tek motor arızasında %200 reaktif moment
5. **Termal:** -20°C ile +60°C arasında ısıl genleşme gerilmeleri

**Emniyet Faktörleri:**
```
CFRP: SF_static = 2.0 (çarpma hasarı toleransı nedeniyle)
Al Alaşım: SF_static = 1.5
Bağlantı Elemanları: SF_static = 3.0 (kritik bağlantılar)
```

### 4.3 Topoloji Optimizasyonu Hedefleri

- Gövde optimizasyonu: %30-45 ağırlık azaltımı hedefi
- Motor kolu: %20-35 ağırlık azaltımı (kesit optimizasyonu)
- Yazılım araçları: Altair OptiStruct, ANSYS Topology Opt., OpenLattice

---

## Adım 5 – Güç Sistemi Detayı

### 5.1 Opsiyon 1: Tam Elektrikli

**Motor Seçimi:**
```
Her rotor için:
T_rotor = 2315 N (elektrikli)
Motor gücü = T × v_induced ≈ T × √(T/2ρA) / η
Tahmini güç per motor: 25-35 kW
Motor tipi: PMSM/BLDC (yüksek tork, düşük KV)
KV değeri: 50-150 RPM/V (büyük rotor için)
Tavsiye edilen: Hacker, Tiger Motor, T-Motor U15 serisi veya muadili
```

**Batarya Sistemi:**
```
Tip: LiPo 6S veya 12S veya LiFePO4
Toplam kapasite: 80-120 kWh
Nominal gerilim: 44.4 V (12S LiPo) veya 72V custom
Hücre sayısı: 500-800 hücre (paralel/seri kombinasyon)
BMS: Aktif dengeleme, termal yönetim zorunlu
C-rating: 10-15C discharge capability
Koruma: IP65, termal izolasyon
```

**ESC Sistemi:**
```
Her motor için ayrı ESC veya merkezi güç dağıtım
ESC güç sınıfı: 40-50 kW continuous
Verimlilik: ≥%96 (SiC MOSFET teknolojisi)
CAN-bus veya UAVCAN haberleşme
```

### 5.2 Opsiyon 2: Hibrit Güç Sistemi

**Jeneratör Ünitesi:**
```
Tip: Wankel rotary engine + axial flux generator
  VEYA: Gasturbine micro-turboşaft + PMSG
Çıkış gücü: 150-200 kW continuous
Yakıt: Jet-A / Diesel / Benzin
Özgül güç hedefi: >1 kW/kg
```

**Güç Yönetim Sistemi (EMS):**
```
Mod 1 – Normal Görev: ICE jeneratör primer, batarya tampon
Mod 2 – Peak Demand (kalkış/manevra): ICE + Batarya paralel
Mod 3 – Sessiz Operasyon: Sadece batarya (≤15 dk)
Mod 4 – Acil: Motor arızasında tek jeneratör güç azaltımı

Batarya tampon: 20-30 kWh (peak shaving için)
```

---

## Adım 6 – Aviyonik ve Kontrol Sistemi

```
Uçuş Kontrol Bilgisayarı: Dual-redundant (Pixhawk, VectorNav, veya özel)
IMU: Triple-redundant MEMS IMU + barometer
GNSS: Dual-band RTK GPS + GLONASS
Optik Akış: Düşük irtifa hover stabilizasyonu
ADS-B: Transponder (SAIL IV için zorunlu)
Batarya/Güç İzleme: CAN-bus entegrasyonlu BMS
Haberleşme: 4G LTE + RF backup (900 MHz / 2.4 GHz)
Payload Arayüzü: MIL-STD-1760 uyumlu elektrik arayüzü
GCS: Ground Control Station, 10 km+ telemetri
```

---

## Adım 7 – Regülasyon Uyumluluğu

### EASA SORA / SAIL IV Gereksinimleri

| OSO # | Gereksinim | Uyumluluk Yöntemi |
|-------|------------|-------------------|
| OSO-01 | Operatör yetkinliği | Sertifikalı pilot + GCS operatörü |
| OSO-02 | UAS yetkinliği | CDR dokümanları + Flight test raporu |
| OSO-03 | Hava durumu kısıtlamaları | OFZ ve meteoroloji entegrasyonu |
| OSO-05 | HMI tasarımı | GCS insan faktörleri analizi |
| OSO-07 | İHA sağlık izleme | BMS + motor telemetri sistemi |
| OSO-10 | Emniyet pilotu | Optik görüş menzili veya FPV + ayrı güvenlik pilotu |
| OSO-12 | İniş sahası yönetimi | Güvenli iniş noktası prosedürü |
| OSO-14 | Acil durum prosedürleri | Parachute / ballistic recovery sistemi |
| OSO-20 | Yazılım kalite güvencesi | DO-178C / EUROCAE ED-12C Level C |
| OSO-23 | Güvenlik güvencesi | Sistem güvenlik analizi (SSA, FMEA) |

### SHGM (Türkiye) Gereksinimleri

- UAS tescili ve operasyon izni
- BVLOS operasyon için özel izin gereklidir
- Kalabalık alanlar üzerinde uçuş için özel değerlendirme

---

## Adım 8 – Risk Analizi ve FMEA

### Kritik Arıza Modları

| Arıza Modu | Etkisi | Tespit Yöntemi | Azaltma Stratejisi |
|------------|--------|----------------|-------------------|
| Çoklu motor arızası (≥2) | Kontrol kaybı | IMU + motor telemetri | 6+ rotor redundancy, parachute |
| Batarya termal kaçak | Yangın/patlama | BMS sıcaklık izleme | Termal izolasyon, CO₂ söndürme |
| GNSS kaybı | Navigasyon hatası | Dual GNSS + optik akış | GNSS-bağımsız mod aktif |
| Geçiş başarısızlığı (VTOL→FW) | Kontrol sorunları | Hız sensörü, kanat pozisyon | Yedek geçiş profili, irtifa rezervi |
| Payload serbest düşme | Yer hasarı | Yük kilitleme sensörü | Dual-lock mekanizması, güvenli bölge |
| ICE motor durması (hibrit) | Güç azalması | RPM sensörü | Batarya yedek mod otomatik devreye |

---

## Adım 9 – .docx Tasarım Raporu Üretimi

### Rapor Yapısı (Her Opsiyon İçin Ayrı veya Birleşik)

Aşağıdaki komutu çalıştırarak raporu oluştur. Önce DOCX skill'ini oku:
`view /mnt/skills/public/docx/SKILL.md`

#### Bölüm 1: Executive Summary
- Senaryo tanımı ve KPI karşılaştırma tablosu (Opsiyon 1 vs. Opsiyon 2)
- MTOW, güç ihtiyacı, menzil, uçuş süresi, maliyet tahmini
- Özet tavsiye (güçlü/zayıf yön analizi)

#### Bölüm 2: Teknik Tasarım Detayları
- Konfigürasyon diyagramı (SVG/ASCII sanat veya açıklama)
- Aerodinamik analiz tabloları
- Güç sistemi şeması
- Bileşen listesi (BOM – Bill of Materials)

#### Bölüm 3: Simülasyon ve Analiz Sonuçları
- FEA özeti (beklenen gerilme, deformasyon, emniyet faktörleri)
- Aerodinamik performans grafiği (tablo formatında)
- Enerji yönetim profili (takeoff → cruise → hover → landing)
- Termal analiz özeti

#### Bölüm 4: Üretim, Doğrulama ve Regülasyon Planı
- Üretim yöntemleri (CFRP layup, CNC, 3D baskı)
- Doğrulama test matrisi
- EASA SORA SAIL IV uyumluluk tablosu
- Kritik tasarım riskleri ve azaltma planı

---

## Adım 10 – JavaScript ile .docx Oluşturma

```bash
# Kurulum
npm install -g docx

# Raporu oluştur
node /home/claude/generate_tandem_cdr_report.js
```

Rapor dosyasını oluştururken:
- A4 sayfa boyutu kullan (11906 × 16838 DXA)
- Türkçe karakter desteği için UTF-8 encoding
- Başlıklar: Heading1 (bölüm), Heading2 (alt bölüm)
- Tablolar: Her sütun için DXA genişlik tanımla
- Renk şeması: Lacivert (#1F3A6E) başlık, açık mavi (#D5E8F0) tablo başlığı
- Footer: Proje adı + sayfa numarası

---

## Referans Değerler ve Kıyaslama Veritabanı

Referans dosyaya bakın: `references/design_parameters_db.md`

Bu dosya şunları içerir:
- Motor veritabanı (KV, güç, verimlilik)
- Batarya kimyasal karşılaştırması
- CFRP vs. Al alaşım mekanik özellikleri
- Tandem Wing tasarım örnekleri (JOBY, Lilium, Pipistrel benzeri)
- Regülasyon referansları (EASA AMC/GM)

---

## Kalite Kontrol Kontrol Listesi

Tasarım raporu teslim etmeden önce şunları doğrula:

- [ ] MTOW hesabı üç yöntemle tutarlı (oran tabanlı, enerji tabanlı, itme tabanlı)
- [ ] Her opsiyon için itme/ağırlık oranı (T/W) ≥ 1.3 (hover güvenliği)
- [ ] Batarya/yakıt ağırlığı toplam sistem ağırlığının %40'ını geçmiyor
- [ ] Kanat yükleme hesabı (W/S) kabul edilebilir aralıkta (80-150 kg/m²)
- [ ] FEA yük durumları regulatory gereksinimlerle eşleşiyor
- [ ] FMEA kritik arıza modlarını kapsıyor
- [ ] EASA SORA OSO'ları adreslenmiş
- [ ] .docx doğrulamadan geçti (`python scripts/office/validate.py`)
- [ ] BOM tamlık kontrolü yapıldı

---

## Örnek Çıktı Özeti (Beklenen Sonuçlar)

| Metrik | Opsiyon 1 (Elektrikli) | Opsiyon 2 (Hibrit) |
|--------|----------------------|-------------------|
| MTOW | ~1400-1500 kg | ~1100-1250 kg |
| Uçuş Süresi | ~20-30 dk | ~90-150 dk |
| Menzil | ~30-50 km | ~150-300 km |
| Ses Seviyesi | Düşük | Orta-Yüksek |
| Bakım Karmaşıklığı | Düşük | Yüksek |
| Başlangıç Maliyeti | Orta | Yüksek |
| İşletme Maliyeti | Düşük (elektrik) | Orta (yakıt) |
| Regülasyon Uyumu | Daha kolay | ICE sertifikasyonu gerekli |
| Tavsiye Kullanım | Kısa menzil/acil müdahale | Uzun menzil/geniş alan |
