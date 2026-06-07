# 🚁 WBS 1.1 — LLM GİRDİ PARAMETRELERİ DETAY REHBERİ

> **Multikopter tasarımında LLM ajanının kullanıcıdan alması gereken tüm parametreler.**
> 10 Kategori | 78 Parametre | JARUS SORA v2.5 + EASA (EU) 2019/945+947 uyumlu

---
## 🔴🟡🟢🔵 Zorunluluk Seviyeleri

| Renk | Seviye | Tanım |
|------|--------|-------|
| 🔴 | **ZORUNLU** | Bu parametre olmadan MDAO başlamaz. Kullanıcı cevap vermeden ilerleme. |
| 🟡 | **ÖNERİLEN** | Tasarım kalitesini artırır; makul varsayılan uygulanabilir. |
| 🟢 | **OPSİYONEL** | Varsa kullanılır; yoksa tablo varsayılanı devreye girer. |
| 🔵 | **KOŞULLU** | Yalnızca belirli görev tipleri veya koşullarda sorulur. |

---
## 📋 LLM SORU SIRASI — Özet (Zorunlulardan Başla)

```
ADIM 1: Önce tüm ZORUNLU (🔴) soruları sor
ADIM 2: ZORUNLU cevap eksik kalırsa tekrar sor (max 3 deneme)
ADIM 3: 3 denemede de cevap gelmezse → escalation_report üret
ADIM 4: ÖNERİLEN soruları sor (kullanıcı 'geç' diyebilir → varsayılan)
ADIM 5: OPSİYONEL ve KOŞULLU soruları konuya göre sor
ADIM 6: Pydantic doğrulama → mission_profile.json kaydet
```

---
## 1. GÖREV TİPİ & UYGULAMA SENARYOSU

| No | Parametre | Birim | Zorunluluk | Varsayılan | LLM'nin Sorusu |
|-----|-----------|-------|------------|------------|----------------|
| 1.1 | **Birincil Görev Tipi** | — | 🔴 ZORUNLU | `—` | Bu multikopter hangi amaçla kullanılacak? (Örn: tarım ilaçlama, kargo teslimat) |
| 1.2 | **Görev Profili Tanımı** | — | 🔴 ZORUNLU | `—` | Görev profilinizi kısaca anlatın. Nerede, ne zaman, nasıl uçacak? |
| 1.3 | **Operasyon Adedi (Günlük/Yıllık)** | uçuş/gün | 🟡 ÖNERİLEN | `1` | Günde kaç uçuş planlanıyor? Bu sayı sistemi nasıl etkiler? |
| 1.4 | **Görev Tekrar Karakteri** | — | 🟡 ÖNERİLEN | `sabit_rota` | Her uçuş aynı güzergahı mı takip ediyor, yoksa değişiyor mu? |
| 1.5 | **Nihai Müşteri / Paydaş** | — | 🟢 OPSİYONEL | `—` | Bu sistem kim için tasarlanıyor? Paydaşlar kim? |

**Detaylar:**
- **1.1 Birincil Görev Tipi**: Sistemin ana kullanım amacı  
  - Örnek: `kargo_teslimat | tarım_ilaçlama | gözetleme_izleme | arama_kurtarma | harita_çık`
  - Kısıt: Liste dışı → kullanıcıdan özelleştirme iste
  - Standart: ASTM F3002-14a §4 | ISO 21384-3:2023
- **1.2 Görev Profili Tanımı**: Görevin doğal dil açıklaması (ConOps girişi)  
  - Örnek: `Şehir merkezinde paket teslimatı — 2 km yarıçap, 5 kg kargo, 20 dak hover`
  - Kısıt: Belirsiz ifadeler → LLM açıklama sorusu üretir
  - Standart: JARUS SORA v2.5 Step#1 | FAA AC 107-2B §5
- **1.3 Operasyon Adedi (Günlük/Yıllık)**: Günlük veya yıllık planlanan uçuş operasyonu sayısı  
  - Örnek: `10 uçuş/gün`
  - Kısıt: Yüksek frekans → redundancy gereksinimi artar
  - Standart: JARUS SORA OSO#01 | EASA AMC RPAS.1309
- **1.4 Görev Tekrar Karakteri**: Her görev aynı mı yoksa değişken mi?  
  - Örnek: `sabit_rota | değişken_rota | otonom_adaptif`
  - Kısıt: Değişken rota → adaptif kontrol ve planlama gerektirir
  - Standart: ISO 21384-3 | JARUS SORA ConOps §2.1
- **1.5 Nihai Müşteri / Paydaş**: Sistemi kim kullanacak / kim için tasarlanıyor?  
  - Örnek: `Kargo firması | Belediye | Tarım kooperatifi | Savunma kurumu`
  - Kısıt: Paydaş belirler → sertifikasyon yolu
  - Standart: INCOSE SE Handbook v4 §4.1

---
## 2. PLATFORM & FİZİKSEL KISITLAR

| No | Parametre | Birim | Zorunluluk | Varsayılan | LLM'nin Sorusu |
|-----|-----------|-------|------------|------------|----------------|
| 2.1 | **Maksimum Kalkış Ağırlığı (MTOW)** | kg | 🔴 ZORUNLU | `—` | Sistemin maksimum ağırlığı (payload dahil) kaç kg olmalı? |
| 2.2 | **Maksimum Gövde Boyutu (Wheelbase / Çapraz)** | m | 🟡 ÖNERİLEN | `—` | Sistemin taşıması veya depolanması için boyut kısıtı var mı? |
| 2.3 | **Gövde Form Faktörü** | — | 🟢 OPSİYONEL | `WBS1.5_trade_off` | Tercih ettiğiniz frame tipi var mı? (Quad, Hex, Octo) |
| 2.4 | **Kol Katlanabilirlik** | — | 🟡 ÖNERİLEN | `False` | Taşıma/depolama için kolların katlanabilir olması gerekiyor mu? |
| 2.5 | **Yük (Payload) Kütlesi** | kg | 🔴 ZORUNLU | `0.0` | Kaç kg payload taşınacak? (kargo, kamera, sensör vs.) |
| 2.6 | **Payload Geometrisi & Montaj Noktası** | mm (L×W×H) + tip | 🟡 ÖNERİLEN | `—` | Payload'ın boyutları ve bağlantı şekli nedir? |
| 2.7 | **Güç Kaynağı Tipi** | — | 🔴 ZORUNLU | `lipo_batarya` | Sistemin enerji kaynağı ne olacak? (LiPo, Li-Ion, Tether?) |
| 2.8 | **Yedek / Redundancy Seviyesi** | — | 🔴 ZORUNLU | `N+1` | Kaç motor arızasında güvenli uçuş/iniş sağlanmalı? |
| 2.9 | **IP Koruma Sınıfı** | — | 🟡 ÖNERİLEN | `IP43` | Hangi hava koşullarında çalışacak? (Yağmur, toz, nem?) |

**Detaylar:**
- **2.1 Maksimum Kalkış Ağırlığı (MTOW)**: Tüm bileşenler dahil toplam maksimum ağırlık  
  - Örnek: `8.5 kg`
  - Kısıt: 0.5–25 kg (EASA Open Cat. C2 limiti 25 kg)
  - Standart: EASA (EU) 2019/945 Madde 20 | ASTM F3002-14a
- **2.2 Maksimum Gövde Boyutu (Wheelbase / Çapraz)**: Motorlar arası çapraz mesafe veya en büyük dış boyut  
  - Örnek: `0.55 m`
  - Kısıt: Fiziksel kısıt: taşıma/depolama; EASA boyut sınıfı
  - Standart: EASA (EU) 2019/945 Madde 20 | JARUS SORA Annex F §3
- **2.3 Gövde Form Faktörü**: Çerçeve/gövde tasarım tercihi  
  - Örnek: `quadcopter_X | hexacopter_X | hexacopter_Y6_coax | octocopter_X8 | octocopter_co`
  - Kısıt: Belirtilmemişse WBS 1.5 trade-off ile belirlenir
  - Standart: NDARC NASA/TM-2015-218751 | Prouty Rotorcraft
- **2.4 Kol Katlanabilirlik**: Kollar katlanabilir mi?  
  - Örnek: `True | False`
  - Kısıt: True → katlanabilir tasarım; ağırlık artışı ~5%
  - Standart: MIL-HDBK-516C §1 | taşıma gereksinimi
- **2.5 Yük (Payload) Kütlesi**: Taşınacak ürün/sensör/ekipman kütlesi  
  - Örnek: `2.0 kg`
  - Kısıt: payload_fraction = m_payload/MTOW ≥ 0.15 (KK-tasarım)
  - Standart: ASTM F3002-14a | Raymer §17 | NDARC
- **2.6 Payload Geometrisi & Montaj Noktası**: Payload'ın fiziksel boyutu ve nasıl bağlanacağı  
  - Örnek: `300×200×150 mm; alt gimbal; quick-release`
  - Kısıt: CG kaymasına etkisi hesaplanmalı (Δcg ≤ 3 mm)
  - Standart: EASA SC-VTOL §2550 | MIL-STD-1760
- **2.7 Güç Kaynağı Tipi**: Enerji kaynağı  
  - Örnek: `lipo_batarya | liion_batarya | lifepo4 | hibrit_yakıt_pil | hidrojen_yakıt_pili `
  - Kısıt: Tether → menzil sıfır; hibrit → daha uzun süre
  - Standart: ASTM F3005-14a | IEC 62619 | UN 38.3
- **2.8 Yedek / Redundancy Seviyesi**: Kaç motor arızasına dayanabilmeli?  
  - Örnek: `N (yedek yok) | N+1 (1 motor arızası) | N+2 (2 motor arızası) | N+2_full`
  - Kısıt: BVLOS → minimum N+1; kritik görev → N+2
  - Standart: EASA SC-VTOL §2530 | JARUS SORA OSO#14
- **2.9 IP Koruma Sınıfı**: Sistemin çevre koruması  
  - Örnek: `IP43 | IP54 | IP65 | IP67 | özelleştirme`
  - Kısıt: Yağmurlu operasyon → min IP54; su üstü → IP65+
  - Standart: IEC 60529 | MIL-STD-810H | DO-160G §4

---
## 3. PERFORMANS GEREKSİNİMLERİ

| No | Parametre | Birim | Zorunluluk | Varsayılan | LLM'nin Sorusu |
|-----|-----------|-------|------------|------------|----------------|
| 3.1 | **Hedef Hover Süresi (Endurance)** | dakika | 🔴 ZORUNLU | `—` | Tek görev için kaç dakika havada kalması gerekiyor? |
| 3.2 | **Maksimum İleri Uçuş Hızı** | m/s | 🔴 ZORUNLU | `—` | Maksimum uçuş hızı kaç m/s (ya da km/h) olmalı? |
| 3.3 | **Nominal Yatay Menzil** | km | 🔴 ZORUNLU | `—` | Ne kadar mesafede uçuş yapılacak? (VLOS mu, BVLOS mu?) |
| 3.4 | **Maksimum Operasyonel İrtifa (AGL)** | m (AGL) | 🔴 ZORUNLU | `120` | Yerden maksimum kaç metre yüksekte uçacak? |
| 3.5 | **Operasyonel Yer İrtifası (MSL)** | m (MSL) | 🔴 ZORUNLU | `0` | Operasyon yeri deniz seviyesinden kaç m yüksekte? (İstanbul=0, Ankara~850m, Erzurum~1869m) |
| 3.6 | **Tur / Devriye Süresi (Gerekirse)** | dakika | 🟢 OPSİYONEL | `0` | Belirli bir alanda devriye/izleme görevi var mı? Kaç dakika? |
| 3.7 | **Tırmanma / Alçalma Hızı** | m/s | 🟡 ÖNERİLEN | `2.0` | Ne kadar hızlı tırmanma ve alçalma gerekiyor? |
| 3.8 | **Konumlama Doğruluğu** | m (RMS) | 🟡 ÖNERİLEN | `0.5` | Ne kadar hassas konumlama gerekiyor? (Normal GPS mi, RTK mi?) |
| 3.9 | **Minimum Batarya Rezervi** | % | 🔴 ZORUNLU | `20` | İniş sonrasında bataryada kaç % enerji kalmalı? |
| 3.10 | **Thrust/Weight Hedefi** | — | 🟢 OPSİYONEL | `2.0` | Motorların toplam iticinin sistemin ağırlığına oranı kaç olmalı? (minimum 2.0) |

**Detaylar:**
- **3.1 Hedef Hover Süresi (Endurance)**: Görev süresince gerekli hover/uçuş süresi  
  - Örnek: `20 dak`
  - Kısıt: WBS 4.7 enerji bütçesini doğrudan belirler; güvenlik: ×1.2
  - Standart: ASTM F3002-14a | NDARC NASA/TM-2015
- **3.2 Maksimum İleri Uçuş Hızı**: Görev sırasında ulaşılacak en yüksek yatay hız  
  - Örnek: `15 m/s`
  - Kısıt: Mevzuat: BVLOS max hız kısıtı; EASA Open Cat. ≤ 19 m/s
  - Standart: EASA (EU) 2019/947 Art.5 | JARUS SORA §2.3.2
- **3.3 Nominal Yatay Menzil**: Baz istasyonundan maksimum yatay uzaklık  
  - Örnek: `5 km`
  - Kısıt: VLOS → <500 m tipik; BVLOS → C2 link menzili ile sınırlı
  - Standart: JARUS SORA v2.5 §2.3 | FAA Part 107.51
- **3.4 Maksimum Operasyonel İrtifa (AGL)**: Yerden en fazla kaç metre yüksekte uçacak?  
  - Örnek: `120 m`
  - Kısıt: EASA Open Cat. → max 120 m AGL; Özel izin → daha yüksek
  - Standart: EASA (EU) 2019/947 Art.4 | ICAO Doc 8168
- **3.5 Operasyonel Yer İrtifası (MSL)**: Hava alanı veya operasyon yeri deniz seviyesinden yüksekliği  
  - Örnek: `1500 m (Ankara)`
  - Kısıt: Yüksek irtifa → motor/pervane derate; ISA+ düzeltmesi
  - Standart: ICAO Doc 8168 | ISA Standardı | NDARC §3.2
- **3.6 Tur / Devriye Süresi (Gerekirse)**: Belirli bir alanda devriye veya gözetleme süresi  
  - Örnek: `60 dak devriye`
  - Kısıt: Devriye → hoverin yanı sıra ileri uçuş; enerji karma
  - Standart: ASTM F3002-14a | MIL-HDBK-1797B
- **3.7 Tırmanma / Alçalma Hızı**: Dikey hız gereksinimi  
  - Örnek: `3 m/s tırmanma; 2 m/s alçalma`
  - Kısıt: Acil iniş → min 1 m/s; normal operasyon → 2-5 m/s
  - Standart: ADS-33E-PRF Tablo 2 | PX4 MC Position Control
- **3.8 Konumlama Doğruluğu**: Hover veya görev noktasında konumlama hassasiyeti  
  - Örnek: `±0.5 m (GPS+EKF) | ±0.1 m (RTK)`
  - Kısıt: Hassas iniş, ilaçlama → RTK; genel gözetleme → GPS
  - Standart: RTCA DO-365 | DO-316A | IEEE AES
- **3.9 Minimum Batarya Rezervi**: İniş sonrası bataryada kalması gereken minimum şarj  
  - Örnek: `20%`
  - Kısıt: FAA/EASA → min %15–20 rezerv önerir; güvenlik marjı
  - Standart: FAA AC 20-184 | EASA AMC RPAS.1309
- **3.10 Thrust/Weight Hedefi**: Tasarımcının öngördüğü T/W oranı (KK-1 sınırı)  
  - Örnek: `2.2`
  - Kısıt: Minimum 2.0 (KK-1); yüksek manevra → 2.5+
  - Standart: Raymer §17 | NDARC | Quan Multicopter Design

---
## 4. OPERASYONEL ÇEVRE

| No | Parametre | Birim | Zorunluluk | Varsayılan | LLM'nin Sorusu |
|-----|-----------|-------|------------|------------|----------------|
| 4.1 | **Coğrafi Operasyon Bölgesi** | — | 🔴 ZORUNLU | `—` | Uçuş nerede gerçekleşecek? (şehir merkezi, kırsal, deniz üstü?) |
| 4.2 | **Engel / Obstacle Ortamı** | — | 🔴 ZORUNLU | `—` | Uçuş ortamında binalar, ağaçlar, enerji hatları var mı? |
| 4.3 | **Hava Sahası Sınıfı** | — | 🔴 ZORUNLU | `G_sınıfı` | Hangi hava sahasında uçacak? ATC izni gerekiyor mu? |
| 4.4 | **Görüş Hattı** | — | 🔴 ZORUNLU | `VLOS` | Pilot her zaman aracı gözle görebilecek mi? (VLOS mu, BVLOS mu?) |
| 4.5 | **Operasyon Zamanı** | — | 🔴 ZORUNLU | `gündüz` | Gündüz mü, gece mi, yoksa her ikisinde de uçacak? |
| 4.6 | **Nüfus Yoğunluğu (Hedef Bölge)** | kişi/km² | 🔴 ZORUNLU | `—` | Uçuş altındaki nüfus yoğunluğu nasıl? (kırsal, şehir içi?) |
| 4.7 | **Zemin Tipi** | — | 🟡 ÖNERİLEN | `sert_düz` | Kalkış ve iniş hangi zemin tipinde yapılacak? |
| 4.8 | **İnsanlı Hava Aracı Trafiği** | — | 🔴 ZORUNLU | `düşük` | Bu bölgede insanlı uçak veya helikopter trafiği yoğun mu? |

**Detaylar:**
- **4.1 Coğrafi Operasyon Bölgesi**: Uçuşun gerçekleştirileceği alan tipi  
  - Örnek: `kentsel_yoğun | kentsel_seyrek | kırsal | deniz_üstü | ormanlık | dağlık | sanay`
  - Kısıt: Nüfus yoğunluğu → SORA GRC belirleme girdisi
  - Standart: JARUS SORA v2.5 Step#2 | EASA AMC UAS.SPEC.010
- **4.2 Engel / Obstacle Ortamı**: Çevredeki fiziksel engeller  
  - Örnek: `açık_alan | bina_arası | ağaç_gölgesi | enerji_hattı_yakın | dağlık_vadi | karış`
  - Kısıt: Dar geçitler → engellerden kaçınma sistemi zorunlu
  - Standart: DO-365 BVLOS | ASTM F3322-18 | ISO 10218-1
- **4.3 Hava Sahası Sınıfı**: Operasyonun yapılacağı hava sahası sınıfı  
  - Örnek: `G_sınıfı | E_sınıfı | D_sınıfı | kontrollü_özel | kısıtlı_bölge | yasak_bölge_dı`
  - Kısıt: Kontrollü saha → ATC koordinasyonu; ATM/UTM entegrasyon
  - Standart: ICAO Annex 11 | EASA IR 2021/664 | FAA Part 107
- **4.4 Görüş Hattı**: Operatörün insansız aracı görebiliyor mu?  
  - Örnek: `VLOS | EVLOS | BVLOS | otonom_tam`
  - Kısıt: BVLOS → C2 link + UTM + Remote ID zorunlu
  - Standart: EASA (EU) 2019/947 | JARUS SORA §1.3 | FAA Part 107.31
- **4.5 Operasyon Zamanı**: Gündüz mü, gece mi, her ikisi de mi?  
  - Örnek: `gündüz | gece | gece_NAL | 24_saat`
  - Kısıt: Gece operasyonu → NAL ışıklandırma + özel onay
  - Standart: EASA (EU) 2019/947 Art.4 | FAA Part 107.29
- **4.6 Nüfus Yoğunluğu (Hedef Bölge)**: Uçuş bölgesindeki kişi yoğunluğu  
  - Örnek: `seyrek (<10) | orta (10-100) | yoğun (100-1000) | çok_yoğun (>1000)`
  - Kısıt: Doğrudan SORA GRC (1-10) girdisi
  - Standart: JARUS SORA v2.5 Annex F §3.2 | Eurostat nüfus DB
- **4.7 Zemin Tipi**: Kalkış/iniş zemini  
  - Örnek: `sert_düz | çim_zemin | kum_çakıl | beton_platforma | su_yüzeyi | eğimli_yüzey | `
  - Kısıt: Su yüzeyi → deniz ayağı opsiyonu; eğimli → iniş takımı tasarımı
  - Standart: FAR/CS 23.473 | EASA SC-VTOL §2520
- **4.8 İnsanlı Hava Aracı Trafiği**: Operasyon bölgesindeki insanlı uçak yoğunluğu  
  - Örnek: `düşük | orta | yüksek | yakın_havalimanı`
  - Kısıt: Yüksek trafik → ARC-b/c; transponder ve UTM entegrasyon
  - Standart: JARUS SORA v2.5 Step#5 ARC | ICAO Annex 2

---
## 5. HAVA & METEOROLOJİ KOŞULları

| No | Parametre | Birim | Zorunluluk | Varsayılan | LLM'nin Sorusu |
|-----|-----------|-------|------------|------------|----------------|
| 5.1 | **Rüzgar Hızı (Operasyonel)** | m/s (veya Beaufort) | 🔴 ZORUNLU | `7` | Maksimum kaç m/s rüzgarda uçabilmeli? |
| 5.2 | **Rüzgar Gustu (Anlık)** | m/s | 🔴 ZORUNLU | `10` | Anlık şiddetli rüzgar (gust) kaç m/s'ye kadar dayanmalı? |
| 5.3 | **Operasyonel Sıcaklık Aralığı** | °C | 🔴 ZORUNLU | `-10 / +45` | Hangi sıcaklık aralığında çalışacak? (kış, yaz, tropik?) |
| 5.4 | **Nem & Yağış** | % RH / Tip | 🔴 ZORUNLU | `≤%80 kuru` | Nemli veya yağışlı havada kullanılacak mı? |
| 5.5 | **Toz ve Partiküller** | — | 🟡 ÖNERİLEN | `temiz_hava` | Toz, kum veya tuzlu hava ortamı var mı? |
| 5.6 | **Donma / Buz Birikimi** | — | 🟢 OPSİYONEL | `yok` | Dondurucu hava veya icing ortamında kullanılacak mı? |
| 5.7 | **Güneş Işınımı / UV Maruziyeti** | W/m² | 🟡 ÖNERİLEN | `<800` | Yoğun güneş altında (çöl, tropik) kullanılacak mı? |
| 5.8 | **Yüksek Rakım ISA Sapması** | °C (ISA farkı) | 🔴 ZORUNLU | `ISA+15` | En yüksek sıcaklıkta (sıcak yaz günü) uçacak mı? Standart havadan ne kadar sapma? |

**Detaylar:**
- **5.1 Rüzgar Hızı (Operasyonel)**: Sistemin normal çalışacağı maksimum rüzgar hızı  
  - Örnek: `10 m/s (Bf4)`
  - Kısıt: Rüzgar direnci → T/W ve aerodinamik tasarımı etkiler
  - Standart: Beaufort Ölçeği | EASA AMC RPAS.1309 §3.4
- **5.2 Rüzgar Gustu (Anlık)**: Anlık en şiddetli rüzgar değeri  
  - Örnek: `15 m/s (3 saniyelik gust)`
  - Kısıt: Gust tepki analizi (WBS 5.4) için doğrudan girdi
  - Standart: MIL-SPEC-8785C | Dryden PSD | EASA CS-23
- **5.3 Operasyonel Sıcaklık Aralığı**: Sistemin çalışacağı hava sıcaklığı aralığı  
  - Örnek: `-10°C … +50°C`
  - Kısıt: Motor, ESC, batarya ve aviyonik thermal marjı
  - Standart: DO-160G §4 | MIL-STD-810H Method 501/502 | IEC 62619
- **5.4 Nem & Yağış**: Çalışma ortamının nem ve yağış durumu  
  - Örnek: `%95 RH | Hafif yağmur (IP54) | Kar`
  - Kısıt: Yağmur → IP54+; nem → konektör ve PCB koruması
  - Standart: DO-160G §14 | MIL-STD-810H Method 507 | IEC 60529
- **5.5 Toz ve Partiküller**: Çevresel toz, kum, tuz (deniz/sanayi ortamı)  
  - Örnek: `temiz_hava | hafif_toz | kum_fırtınası | tuz_sisi | sanayi_emisyonu`
  - Kısıt: Toz → filtre ve IP; tuz → korozyon koruma
  - Standart: DO-160G §12 | MIL-STD-810H Method 510 | IP6X
- **5.6 Donma / Buz Birikimi**: Donma riski / buz birikimi (icing) koşulu  
  - Örnek: `donma_riski_yok | islak_kar | hafif_icing (<-5°C)`
  - Kısıt: Icing → pervane ısıtma veya özel kaplama; batarya soğuması
  - Standart: DO-160G §24 | FAA AC 91-74B
- **5.7 Güneş Işınımı / UV Maruziyeti**: Yoğun güneş ışığı ve UV altında operasyon  
  - Örnek: `1000 W/m² (tropikal)`
  - Kısıt: Batarya ısınması; polimer bileşen degradasyonu
  - Standart: DO-160G §23 | MIL-STD-810H Method 505
- **5.8 Yüksek Rakım ISA Sapması**: Standart atmosferden yüksek irtifa sapması  
  - Örnek: `ISA+25°C (sıcak gün) | ISA-15°C (soğuk)`
  - Kısıt: ISA+ → motor derate; ISA- → batarya kapasitesi düşer
  - Standart: ICAO Doc 8168 | ISA Standard Atmosphere | NDARC §3

---
## 6. MEVZUAT & RİSK PROFİLİ

| No | Parametre | Birim | Zorunluluk | Varsayılan | LLM'nin Sorusu |
|-----|-----------|-------|------------|------------|----------------|
| 6.1 | **Hedef Mevzuat Ülkesi** | — | 🔴 ZORUNLU | `—` | Sistem hangi ülkede/bölgede kullanılacak? |
| 6.2 | **EASA Kategori Hedefi** | — | 🔴 ZORUNLU | `—` | Hangi EASA kategorisini hedefliyorsunuz? (Open A1/A2/A3, Specific?) |
| 6.3 | **BVLOS Operasyon Planı** | — | 🔴 ZORUNLU | `False` | Pilot görüş hattı dışında (BVLOS) uçuş planlanıyor mu? |
| 6.4 | **Hedeflenen SAIL Seviyesi** | — | 🟡 ÖNERİLEN | `bilinmiyor` | SORA kapsamında hangi risk seviyesi (SAIL) bekleniyor? |
| 6.5 | **Üçüncü Taraf Risk Toleransı** | — | 🔴 ZORUNLU | `1e-7_FH` | Uçuş altındaki insanlar için kabul edilebilir risk eşiği nedir? |
| 6.6 | **Remote ID Gereksinimi** | — | 🔴 ZORUNLU | `True` | Remote ID (uzaktan kimlik yayını) zorunlu mu? |
| 6.7 | **Sertifikasyon Zaman Çerçevesi** | ay | 🟢 OPSİYONEL | `—` | Sertifikasyon için ne kadar süreniz var? |
| 6.8 | **DO-160G Çevre Kategori Sınıfı** | — | 🟡 ÖNERİLEN | `Kategori_B` | Bileşenlerin DO-160G sertifikasyon kategorisi nedir? |

**Detaylar:**
- **6.1 Hedef Mevzuat Ülkesi**: Operasyonun gerçekleştirileceği ülke/bölge mevzuatı  
  - Örnek: `EASA_AB | FAA_USA | TCAA_Türkiye | CAA_UK | DGCA_Hindistan | diğer`
  - Kısıt: Ülke belirler → hangi standart zinciri uygulanacak
  - Standart: EASA (EU) 2019/945+947 | FAA Part 107 | SHGM Reg.
- **6.2 EASA Kategori Hedefi**: Hedeflenen EASA UAS operasyon kategorisi  
  - Örnek: `Open_A1 | Open_A2 | Open_A3 | Specific_STS01 | Specific_STS02 | Specific_PDRA | `
  - Kısıt: Kategori → sertifikasyon yükünü belirler
  - Standart: EASA (EU) 2019/947 Art.4-6 | AMC UAS.SPEC.010
- **6.3 BVLOS Operasyon Planı**: BVLOS operasyonu planlanıyor mu?  
  - Örnek: `True | False`
  - Kısıt: True → C2 link, Remote ID, UTM, osO#10+11 zorunlu
  - Standart: JARUS SORA v2.5 | EASA AMC UAS.SPEC.060 | DO-365
- **6.4 Hedeflenen SAIL Seviyesi**: SORA sürecinde hedeflenen SAIL skoru  
  - Örnek: `SAIL-I | SAIL-II | SAIL-III | SAIL-IV | SAIL-V | SAIL-VI | bilinmiyor`
  - Kısıt: Bilinmiyorsa LLM GRC ve ARC değerlendirmesiyle hesaplar
  - Standart: JARUS SORA v2.5 Table 5 | EASA UAS SAIL
- **6.5 Üçüncü Taraf Risk Toleransı**: Uçuş altındaki insanlara verilen risk toleransı  
  - Örnek: `TLOS_eşdeğeri | 1e-6_FH | 1e-7_FH | daha_düşük`
  - Kısıt: Yüksek nüfus → düşük risk toleransı → FTA gereksinimi
  - Standart: JARUS SORA v2.5 §2.3 | ARP4761A
- **6.6 Remote ID Gereksinimi**: Uzaktan kimlik yayını zorunlu mu?  
  - Örnek: `True | False`
  - Kısıt: EASA → tüm kategorilerde; FAA → Part 107 →Remote ID zorunlu
  - Standart: ASTM F3411-22a | EASA (EU) 2022/425 | FAA 14 CFR §89
- **6.7 Sertifikasyon Zaman Çerçevesi**: Sertifikasyon süreci için planlanan süre  
  - Örnek: `18 ay`
  - Kısıt: Kısa süre → daha az kompleks tasarım; standart STS tercih
  - Standart: EASA AMC UAS.SPEC.010 | JARUS SORA süreç tablosu
- **6.8 DO-160G Çevre Kategori Sınıfı**: Elektronik ve yapısal bileşenler için test kategorisi  
  - Örnek: `Kategori_A | Kategori_B | Kategori_C | Kategori_D`
  - Kısıt: Kategori C/D → daha sert test; sertifikasyon yüküne eklenir
  - Standart: DO-160G §1.5 | RTCA/DO-160G

---
## 7. PAYLOAD & SENSÖR SİSTEMİ

| No | Parametre | Birim | Zorunluluk | Varsayılan | LLM'nin Sorusu |
|-----|-----------|-------|------------|------------|----------------|
| 7.1 | **Payload Tipi** | — | 🔴 ZORUNLU | `—` | Taşınacak yük/sensör nedir? (kamera, kargo, ilaçlama?) |
| 7.2 | **Payload Güç Tüketimi** | W | 🔴 ZORUNLU | `0` | Payload kaç Watt güç tüketiyor? |
| 7.3 | **Payload Veri Arayüzü** | — | 🟡 ÖNERİLEN | `MAVLink` | Payload hangi protokol/arayüz ile bağlanacak? |
| 7.4 | **Stabilizasyon Gereksinimi** | — | 🟡 ÖNERİLEN | `sabit_montaj` | Kamera veya sensörün titreşim izolasyonu veya gimbalı var mı? |
| 7.5 | **Teslimat / Bırakma Mekanizması** | — | 🔵 KOŞULLU | `yok` | Kargo/paket bırakma mekanizması var mı? Nasıl çalışıyor? |
| 7.6 | **Veri Depolama & İletim** | — | 🟡 ÖNERİLEN | `SD_kart_yerel` | Veri yerel mi saklanacak, yoksa canlı mı iletilecek? |

**Detaylar:**
- **7.1 Payload Tipi**: Taşınacak ekipmanın tipi  
  - Örnek: `kargo_paketi | RGB_kamera | termal_kamera | multispektral_kamera | lidar_3D | sa`
  - Kısıt: Tip → bağlantı arayüzü ve CG etkisini belirler
  - Standart: EASA SC-VTOL §2550 | MIL-STD-1760 | DO-160G §1
- **7.2 Payload Güç Tüketimi**: Payload'ın sürekli ve tepe güç çekimi  
  - Örnek: `Kamera: 15 W | Lidar: 25 W | İlaçlama pompası: 50 W`
  - Kısıt: Enerji bütçesine (WBS 4.7) eklenir
  - Standart: MIL-STD-704F | DO-160G §16
- **7.3 Payload Veri Arayüzü**: Payload ile uçuş bilgisayarı veri bağlantı tipi  
  - Örnek: `MAVLink | UART | I2C | SPI | Ethernet | CAN | USB | analog | kablosuz_video | öz`
  - Kısıt: Arayüz → yazılım entegrasyonu ve veri gecikmesini belirler
  - Standart: MAVLink 2.0 | CAN FD | DO-160G §20
- **7.4 Stabilizasyon Gereksinimi**: Payload'ın gimbal/stabilizasyon ihtiyacı  
  - Örnek: `3_eksen_gimbal | 2_eksen_gimbal | sabit_montaj | aktif_titreşim_izolasyon`
  - Kısıt: Gimbal → ek kütle +200-500 g; servo güç +15W
  - Standart: MIL-STD-810H Method 514 | Sony/DJI gimbal specs
- **7.5 Teslimat / Bırakma Mekanizması**: Payload'ı bırakma veya teslimat sistemi  
  - Örnek: `vinç_mekanizması | serbest_bırakma | paket_itici | yok`
  - Kısıt: Teslimat → CG kayması analizi; mekanizma ağırlığı +200-800 g
  - Standart: EASA SC-VTOL §2555 | FAA UAS Delivery waivers
- **7.6 Veri Depolama & İletim**: Payload verilerinin nasıl saklanacağı/iletileceği  
  - Örnek: `SD_kart_yerel | LTE_canlı | WiFi_yakın | 4G_5G_bulut | şifreli_link | video_down`
  - Kısıt: Canlı stream → datalink bant genişliği gereksinimi
  - Standart: DO-160G §20 | JARUS SORA OSO#10 | EUROCAE ED-269

---
## 8. HABERLEŞme & ALTYAPI

| No | Parametre | Birim | Zorunluluk | Varsayılan | LLM'nin Sorusu |
|-----|-----------|-------|------------|------------|----------------|
| 8.1 | **RC Link Protokolü / Frekans** | MHz | 🔴 ZORUNLU | `2.4GHz_ELRS` | Pilot kontrol için hangi frekans/protokol kullanılacak? |
| 8.2 | **Telemetri & C2 Datalink** | — | 🔴 ZORUNLU | `MAVLink_915MHz` | Telemetri ve komuta linki için hangi teknolojiyi planlıyorsunuz? |
| 8.3 | **GPS / GNSS Konfigürasyonu** | — | 🔴 ZORUNLU | `GPS_L1` | GPS yeterli mi, RTK gerekiyor mu? Anti-spoofing lazım mı? |
| 8.4 | **Uçuş Kontrol Kartı (FC)** | — | 🟡 ÖNERİLEN | `belirlenmedi` | Belirli bir uçuş kontrol kartı veya yazılımı gerekiyor mu? |
| 8.5 | **UTM / U-Space Entegrasyon** | — | 🔵 KOŞULLU | `opsiyonel` | Uçuş yönetim sistemi (UTM) entegrasyonu gerekiyor mu? |
| 8.6 | **Şifreleme / Siber Güvenlik** | — | 🟡 ÖNERİLEN | `AES128` | Komuta-kontrol verisi şifrelenecek mi? |

**Detaylar:**
- **8.1 RC Link Protokolü / Frekans**: Pilot kontrol linkinin protokolü ve frekans bandı  
  - Örnek: `2.4 GHz ELRS | 868 MHz Crossfire | 900 MHz | 5.8 GHz | Herelink | özel`
  - Kısıt: BVLOS → 868/915 MHz tercih (menzil); VLOS → 2.4 GHz yeterli
  - Standart: ETSI EN 300 328 | FCC Part 15 | DO-160G §20
- **8.2 Telemetri & C2 Datalink**: Telemetri sistemi ve komuta-kontrol link tipi  
  - Örnek: `MAVLink_915MHz | MAVLink_LTE | 4G_LTE_primer | LTE_915MHz_yedek | SatCom | özel_`
  - Kısıt: BVLOS → LTE primer + 915 MHz yedek; availability ≥%99.9
  - Standart: JARUS SORA OSO#10 | EUROCAE ED-269 | DO-365
- **8.3 GPS / GNSS Konfigürasyonu**: Kullanılacak uydu navigasyon sistemi  
  - Örnek: `GPS_L1 | GPS_L1_L2 | GPS_GLONASS | GPS_Galileo | RTK_GPS | RTK_çift_anten | anti`
  - Kısıt: RTK → cm hassasiyet; anti-spoofing → BVLOS güvenlik
  - Standart: RTCA DO-316A | EUROCAE ED-127 | FAA AC 20-138D
- **8.4 Uçuş Kontrol Kartı (FC)**: Tercih edilen veya zorunlu uçuş bilgisayarı  
  - Örnek: `Pixhawk6X | Pixhawk6C | Cube_Orange+ | Holybro_H7 | Auterion_Skynode | özel_tasa`
  - Kısıt: FC → PX4 mi ArduPilot mü? Firmware seçimini belirler
  - Standart: PX4 Dev Guide v1.14 | ArduPilot Docs | ChibiOS
- **8.5 UTM / U-Space Entegrasyon**: Uçuş yönetim sistemi entegrasyonu  
  - Örnek: `GUTMA | ASTM_F3411 | EASA_Uspace | opsiyonel | zorunlu_değil`
  - Kısıt: BVLOS veya SAIL-III+ → UTM entegrasyonu zorunlu
  - Standart: ASTM F3411-22a | EASA Reg.2021/664 | ICAO RPAS manual
- **8.6 Şifreleme / Siber Güvenlik**: Haberleşme güvenliği gereksinimi  
  - Örnek: `yok | AES128 | AES256 | FIPS_140_2 | NATO_standardı`
  - Kısıt: Kritik görev veya askeri → FIPS veya NATO standard
  - Standart: NIST SP 800-38A | EUROCAE ED-269 | IEC 62443

---
## 9. GÜVENLİK & ACİL DURUM

| No | Parametre | Birim | Zorunluluk | Varsayılan | LLM'nin Sorusu |
|-----|-----------|-------|------------|------------|----------------|
| 9.1 | **Fallback / Güvenli Uçuş Modu** | — | 🔴 ZORUNLU | `RTL_motor_arıza` | Motor arızasında veya bağlantı kesilince ne yapmalı? |
| 9.2 | **Düşme Koruma Sistemi** | — | 🔵 KOŞULLU | `yok` | Düşme durumunda koruma sistemi (paraşüt vs.) gerekiyor mu? |
| 9.3 | **Geofence / Coğrafi Kısıtlama** | — | 🔴 ZORUNLU | `çember_r=500m` | Uçuş sınırı (geofence) tanımlanacak mı? Nasıl? |
| 9.4 | **İnsanlı Ekip (Remote Crew) Sayısı** | kişi | 🔴 ZORUNLU | `1` | Kaç kişilik operatör ekibi olacak? |
| 9.5 | **Acil Müdahale Planı (ERP)** | — | 🔴 ZORUNLU | `False` | Acil durum müdahale prosedürü (ERP) hazırlandı mı? |
| 9.6 | **Personel Güvenlik Mesafesi** | m | 🔴 ZORUNLU | `30` | Sistemden insanların güvenli mesafesi kaç metre? |

**Detaylar:**
- **9.1 Fallback / Güvenli Uçuş Modu**: Motor arızasında veya link kesilmesinde ne yapacak?  
  - Örnek: `RTL_motor_arıza | otonom_iniş | hover_bekle | paşüt_açma | özel`
  - Kısıt: BVLOS → RTL veya otonom iniş zorunlu; OEI analizi
  - Standart: EASA AMC RPAS.1309 | JARUS SORA OSO#06 | DO-365
- **9.2 Düşme Koruma Sistemi**: Arıza durumunda fiziksel güvenlik sistemi  
  - Örnek: `yok | paraşüt | hava_torbası | ağ_atma | ballistic_parachute`
  - Kısıt: Yüksek GRC → paraşüt gerekebilir; ağırlık etkisi
  - Standart: JARUS SORA §3.2.7 | EASA AMC RPAS.1309 §Annex C
- **9.3 Geofence / Coğrafi Kısıtlama**: Uçuş sınırı/yasak bölge tanımlama  
  - Örnek: `çember_r=500m | poligon | 3D_hacim | dinamik | yok`
  - Kısıt: Her operasyon için minimum basit geofence önerilir
  - Standart: EASA AMC RPAS.1309 | JARUS SORA OSO#05 | DO-365
- **9.4 İnsanlı Ekip (Remote Crew) Sayısı**: Operasyonu kaç kişi yönetecek?  
  - Örnek: `1 pilot + 1 gözlemci`
  - Kısıt: BVLOS → koordinatör; EVLOS → en az 1 gözlemci
  - Standart: JARUS SORA v2.5 §2.4 | EASA ORO.GEN.110
- **9.5 Acil Müdahale Planı (ERP)**: Acil durumda ne yapılacağı prosedürü  
  - Örnek: `True | False; Evet → prosedür özeti`
  - Kısıt: SORA ConOps kapsamında ERP zorunlu
  - Standart: JARUS SORA v2.5 §2.5 ERP | EASA AMC RPAS.1309
- **9.6 Personel Güvenlik Mesafesi**: Operatör ve izleyicilerden minimum güvenli mesafe  
  - Örnek: `30 m`
  - Kısıt: EASA Open → 30 m; Specific → risk bazlı hesap
  - Standart: EASA (EU) 2019/947 Art.4 | JARUS SORA OSO#06

---
## 10. BÜTÇE, ZAMAN & ÖZEL KISITLAR

| No | Parametre | Birim | Zorunluluk | Varsayılan | LLM'nin Sorusu |
|-----|-----------|-------|------------|------------|----------------|
| 10.1 | **Proje Bütçesi (Donanım)** | USD | 🟡 ÖNERİLEN | `—` | Sistemin toplam donanım bütçesi nedir? |
| 10.2 | **Tasarım Teslim Süresi** | ay | 🟡 ÖNERİLEN | `—` | İlk prototip ne zaman hazır olmalı? |
| 10.3 | **Tekrar Üretim Adedi** | adet | 🟡 ÖNERİLEN | `1` | Kaç adet üretilmesi planlanıyor? |
| 10.4 | **Özel Malzeme / Bileşen Kısıtı** | — | 🟢 OPSİYONEL | `—` | Özel malzeme kısıtı var mı? (yerli, ITAR-free, belirli marka?) |
| 10.5 | **Yazılım Mimarisi Tercihi** | — | 🟡 ÖNERİLEN | `PX4` | PX4 mı, ArduPilot mı, özel yazılım mı kullanılacak? |
| 10.6 | **Özel Operasyonel Kısıtlar** | — | 🟢 OPSİYONEL | `—` | Başka özel gereksinim veya kısıt var mı? |
| 10.7 | **Benzer Referans Sistem** | — | 🟢 OPSİYONEL | `yok` | Benzer bir ticari sistem referans alınacak mı? Hangisi? |

**Detaylar:**
- **10.1 Proje Bütçesi (Donanım)**: Toplam donanım maliyeti üst sınırı  
  - Örnek: `5.000 USD | 15.000 USD | 50.000 USD`
  - Kısıt: Bütçe → bileşen seçimini kısıtlar (ticari vs. özel)
  - Standart: AS9102 | ISO 9001:2015 proje kısıt yönetimi
- **10.2 Tasarım Teslim Süresi**: Prototipin hazır olması için gereken süre  
  - Örnek: `6 ay | 12 ay | 24 ay`
  - Kısıt: Kısa süre → ticari bileşen; uzun → özel tasarım
  - Standart: INCOSE SE Handbook v4 §7 proje planlama
- **10.3 Tekrar Üretim Adedi**: Kaç adet üretilecek?  
  - Örnek: `1 prototip | 5 seri | 50 seri | 500+ seri`
  - Kısıt: Seri üretim → BOM maliyet optimizasyonu; imalat süreci
  - Standart: AS9100D | ISO 9001:2015 | MIL-HDBK-516C §1
- **10.4 Özel Malzeme / Bileşen Kısıtı**: Belirli malzeme veya tedarikçi zorunluluğu/yasağı  
  - Örnek: `'Sadece yerel tedarikçi' | 'ITAR bileşen kullanma' | 'CFRP zorunlu'`
  - Kısıt: Yerli tedarik → seçenek kısıtlanır; malzeme seçimi
  - Standart: ITAR (22 CFR §120-130) | EAR | AS9100D §8.4
- **10.5 Yazılım Mimarisi Tercihi**: Uçuş yazılımı tercihi  
  - Örnek: `PX4 | ArduPilot | özel_geliştirme | ROS2_tabanlı | belirlenmedi`
  - Kısıt: Yazılım → GNC tasarımı ve CI/CD altyapısını belirler
  - Standart: PX4 Dev Guide | ArduPilot Docs | DO-178C
- **10.6 Özel Operasyonel Kısıtlar**: Diğer tasarım veya operasyonel özel gereksinimler  
  - Örnek: `'Görsel çıktı şart' | 'Gece görüşü lazım' | 'Ses ≤60 dBA' | 'ITAR-free'`
  - Kısıt: Her özel kısıt tasarıma ekstra gereksinim ekler
  - Standart: Müşteri gereksinim dokümanı | CONOPS
- **10.7 Benzer Referans Sistem**: Referans alınacak mevcut ticari sistem var mı?  
  - Örnek: `DJI Matrice 350 | Freefly Alta X | Acecore NOA | yok`
  - Kısıt: Referans → performans karşılaştırma ve benchmark
  - Standart: Raymer §2 | NDARC benchmarking metodolojisi

---
## 🤖 LLM UYGULAMA KODU (Özet)

```python
from mission_profile_schema import MissionProfile, collect_mission_profile

# Kullanıcının doğal dil girişinden otomatik parametre toplama
user_text = "5 kg kargo taşıyan, 20 dk uçan, şehir içi teslimat dronu"
profile = collect_mission_profile(user_text, llm_agent)

# Pydantic doğrulama otomatik
# mission_profile.json → requirements.json → WBS 1.2'ye geç
```

---
*WBS 1.1 Detay Rehberi v4.0 — Nisan 2026 | 78 Parametre | 10 Kategori*