# Tasarım Parametreleri Referans Veritabanı
# Tandem Wing + MultiCopter CDR Skill için

## İçindekiler
1. Motor Veritabanı
2. Batarya Kimyasal Karşılaştırması
3. Malzeme Mekanik Özellikleri
4. Aerodinamik Profil Verileri
5. Tandem Wing Referans Tasarımları
6. Regülasyon Referansları

---

## 1. Motor Veritabanı (Büyük İHA Sınıfı)

| Motor | Güç (kW) | Max İtme (N) | KV (RPM/V) | Ağırlık (kg) | Verimlilik |
|-------|----------|-------------|-----------|-------------|-----------|
| T-Motor U15 | 8 kW | 3430 N @ 36V | 70 | 1.2 kg | %92 |
| Hacker Q150-4M | 12 kW | ~5000 N | 55 | 1.8 kg | %93 |
| Tiger Motor MN10005 | 6 kW | 2800 N | 90 | 0.95 kg | %90 |
| Emrax 228 (custom) | 35 kW | - (jeneratör) | - | 12 kg | %96 |
| Pipistrel E-811 benzeri | 50 kW | - | - | 16 kg | %95.5 |
| **Hibrit için Jeneratör** | | | | | |
| UAV Turbines PT6 mini | 150 kW shaft | - | - | 45 kg | %28-32 termal |
| Wankel 250cc | 15 kW | - | - | 8 kg | %30 termal |

**Not:** Büyük rotor (D>1.5m) sistemlerde özel PMSM motorlar gerekir. Mevcut piyasa çözümleri
sınırlıdır; custom motor geliştirilmesi CDR'da değerlendirilmelidir.

---

## 2. Batarya Kimyasal Karşılaştırması

| Tip | Enerji Yoğunluğu (Wh/kg) | Güç Yoğunluğu (W/kg) | Çevrim Ömrü | Güvenlik | Maliyet ($/kWh) |
|-----|--------------------------|----------------------|-------------|---------|----------------|
| LiPo (NMC) | 200-260 | 500-2000 | 300-500 | ⚠️ Termal kaçak riski | 150-300 |
| LiFePO4 | 120-165 | 200-500 | 2000-3000 | ✅ Güvenli | 200-400 |
| Li-S (deneysel) | 350-500 | 200-400 | 100-200 | ⚠️ Olgunluk düşük | 800-1500 |
| Solid-State (2026+) | 300-400 | 500-1000 | 1000+ | ✅ Çok güvenli | 500-2000 |
| Hidrojen Yakıt Hücresi | 800-1500* | 100-300 | 5000+ | ⚠️ H₂ depolama | 1000-3000 |

*Sistem ağırlığı dahil 400-600 Wh/kg

**500 kg payload İHA için Tavsiye:**
- Kısa görev: LiPo 6S/12S (max enerji yoğunluğu)
- Uzun ömür: LiFePO4 (güvenlik + ömür)
- Hibrit tampon: LiFePO4 20-30 kWh

---

## 3. Malzeme Mekanik Özellikleri

### Karbon Fiber Kompozit (CFRP)

| Özellik | CFRP UD (T300) | CFRP UD (T700) | CFRP Dokuma | Birim |
|---------|---------------|---------------|-------------|-------|
| Yoğunluk | 1550 | 1580 | 1500 | kg/m³ |
| Çekme Mukavemeti | 1500 | 2550 | 900 | MPa |
| Elastisite Modülü | 135 | 165 | 70 | GPa |
| Özgül Mukavemet | 968 | 1613 | 600 | kN·m/kg |
| Darbe Tokluğu | Düşük | Düşük | Orta | - |
| Maliyet (prepreg) | ~40 $/kg | ~80 $/kg | ~30 $/kg | - |

### Alüminyum Alaşımlar

| Alaşım | Çekme Mukavemeti | Akma Sınırı | Elastisite Mod. | Yoğunluk | Maliyet |
|--------|-----------------|-------------|----------------|---------|---------|
| Al 6061-T6 | 310 MPa | 276 MPa | 68.9 GPa | 2700 kg/m³ | ~3 $/kg |
| Al 7075-T6 | 572 MPa | 503 MPa | 71.7 GPa | 2810 kg/m³ | ~6 $/kg |
| Al 2024-T4 | 470 MPa | 325 MPa | 72.4 GPa | 2780 kg/m³ | ~5 $/kg |

### Titanyum (Ti-6Al-4V)

| Özellik | Değer | Birim |
|---------|-------|-------|
| Çekme Mukavemeti | 950 MPa | - |
| Yoğunluk | 4430 kg/m³ | - |
| Elastisite Modülü | 113.8 GPa | - |
| Yorulma Sınırı | ~550 MPa | - |
| Maliyet | ~30-50 $/kg | - |

**Seçim Kılavuzu:**
- Ana yapı: CFRP T700 (en hafif, yüksek mukavemet)
- Bağlantı parçaları: Al 7075-T6 (makineli işlem kolaylığı + maliyet)
- Titanyum: Kritik bağlantı bulonları, yüksek yorulma noktaları

---

## 4. Aerodinamik Profil Verileri

### NACA 4412 (Önerilen Ana Kanat Profili)

| Parametre | Değer |
|-----------|-------|
| Maksimum CL | 1.65 (Re=6×10⁶) |
| CL/CD (max) | ~80 |
| Stall AoA | ~16° |
| Zero-lift AoA | ~-4° |
| Moment katsayısı Cm0 | -0.093 |
| Uygun Re aralığı | 0.5×10⁶ – 10×10⁶ |

### Clark-Y (Alternatif)

| Parametre | Değer |
|-----------|-------|
| Maksimum CL | 1.47 |
| CL/CD (max) | ~60 |
| Stall AoA | ~15° |
| Zero-lift AoA | ~-5.5° |

### Tandem Wing Aerodinamik Etkileşim

**Önemli Faktörler:**
- Ön kanat downwash, arka kanada çarpar → arka kanat etkin AoA azalır
- Dengeleme: Arka kanat %10-20 daha büyük alan veya daha yüksek CL profili
- Boyuna denge (longitudinal stability): Nötral nokta hesabı zorunlu
  - CG, aerodinamik merkez ile %5-15 arasında olmalı
- İdeal konfigürasyon: Arka kanat biraz daha yüksek montaj açısı (+1° ile +3°)

---

## 5. Tandem Wing Referans Tasarımları

| Platform | MTOW | Payload | Güç | Kanat | Kullanım |
|----------|------|---------|-----|-------|---------|
| Scaled Composites Proteus | 5670 kg | 1800 kg | Turbofan×2 | Tandem | Yüksek irtifa araştırma |
| Quickie Q2 | 499 kg | 2 kişi | Piston 65HP | Tandem | Genel havacılık |
| Beechcraft Starship | 6350 kg | 1315 kg | Turboprop×2 | Tandem | Ticari |
| **İHA Sınıfı (Örnekler)** | | | | | |
| Wingcopter 178 | 30 kg | 5 kg | Elektrikli | Fixed+tilt | Kargo teslimat |
| Joby Aviation S4 | 2177 kg | 4+pilot | Elektrikli | eVTOL | Yolcu |
| Pipistrel Nuuva V300 | 1200 kg | 300 kg | Hibrit | Tandem+copter | Kargo |

**Pipistrel Nuuva V300 En Yakın Referans:**
- 300 kg payload (hedefimizin %60'ı)
- Tandem kanat + 8 lift rotor konfigürasyonu
- Hibrit güç sistemi
- Taşıma kapasitesini %67 artırarak hedefimize ulaşılabilir

---

## 6. Regülasyon Referansları

### EASA UAS Regülasyonları
- EU 2019/945: UAS sınıfı tasarım gereksinimleri
- EU 2019/947: UAS operasyon kuralları
- EASA AMC/GM to UAS Specific Category: SORA metodolojisi
- EASA SC-VTOL: VTOL sertifikasyon standardı (manned, adapted for heavy UAS)

### SAIL Seviye Matrisi (SORA)

| SAIL | GRC | ARC | Açıklama |
|------|-----|-----|---------|
| I | 1 | a | Çok düşük risk |
| II | 2 | a | Düşük risk |
| III | 3 | b | Orta risk |
| **IV** | **4** | **b/c** | **Yüksek risk – Bizim hedefimiz** |
| V | 5 | c | Çok yüksek risk |
| VI | 6 | d | En yüksek risk |

**SAIL IV için Minimum OSO'lar:**
- OSO #1-5: LOW integrity
- OSO #6-10: MEDIUM integrity  
- OSO #11-14, #21-24: LOW integrity

### DO-178C (Yazılım Sertifikasyon)
- Level A: Felaket (Catastrophic) arıza
- **Level B: Tehlikeli (Hazardous) – Uçuş kontrol yazılımı için minimum**
- Level C: Major arıza – Payload kontrol yazılımı
- Level D: Minor arıza – GCS yazılımı

### SHGM (Türkiye) Referanslar
- SHY-İHA: İnsansız Hava Araçları Yönetmeliği
- SHY-6A: Deneysel hava aracı tescil kuralları
- Operasyon izni: SHGM'ye yazılı başvuru + CDR raporları

---

## 7. Maliyet Tahmin Rehberi

### Geliştirme Maliyetleri (Kaba Tahmin)

| Faz | Maliyet Aralığı | Süre |
|-----|----------------|------|
| Sistem Gereksinimler + CDR | 200K-500K USD | 6-12 ay |
| Prototip Üretimi (×1) | 500K-2M USD | 12-18 ay |
| Test ve Sertifikasyon | 300K-1M USD | 12-24 ay |
| **Toplam TRL 6'ya ulaşmak** | **1M-3.5M USD** | **30-54 ay** |

### Birim Üretim Maliyeti (Seri – 10+ adet)

| Bileşen | Elektrikli | Hibrit |
|---------|-----------|--------|
| CFRP yapı | 80-150K USD | 80-150K USD |
| Motor + ESC sistemi | 50-100K USD | 30-60K USD |
| Batarya sistemi | 100-200K USD | 30-60K USD |
| Jeneratör/ICE | - | 80-150K USD |
| Aviyonik | 30-80K USD | 30-80K USD |
| Toplam | **260-530K USD** | **250-500K USD** |
