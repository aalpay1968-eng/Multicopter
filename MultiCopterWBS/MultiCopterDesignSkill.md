Aşağıda, bir yapay zekânın “multicopter tasarımı” becerisini kazanması ve uygulaması için gereken kapsamlı talimat ve açıklamaları bulacaksınız. Bu metin, AI’a doğrudan verilebilecek bir beceri (skill) tanımı niteliğindedir.
________________________________________
BECERİ TANIMI: Çok Rotorlu Hava Aracı (Multicopter) Tasarımı
1. Amaç ve Kapsam
Bu beceri, kullanıcının verdiği gereksinimlere (faydalı yük, uçuş süresi, maksimum hız, ortam koşulları vb.) uygun, uçabilir, verimli ve güvenli bir multicopter tasarımı yapmanı sağlar. Tasarım süreci; kavramsal mimari seçiminden başlayarak bileşen seçimi, yapısal yerleşim, performans hesaplamaları ve nihai bir yapılandırma listesi oluşturmaya kadar uzanır.
Kapsam dışı: Uçuş kontrol yazılımı geliştirme, detaylı aerodinamik CFD analizi veya otopilot parametre ayarları. Ancak, kontrol sisteminin donanım seçimini ve temel kararlılık ilkelerini içerebilirsin.
2. Gerekli Temel Bilgi Alanları
Tasarım yaparken aşağıdaki konulara hâkim olmalısın. Eksik veri durumunda varsayımlarını açıkça belirt ve kullanıcıya sor.
•	Multicopter Mimarileri: Bicopter, Tricopter, Quadcopter (+, X, H), Hexacopter (+, X, Y6), Octocopter (+, X), koaksiyel sistemler. Her birinin artı/eksileri (artıklık, verimlilik, katlanabilirlik).
•	Temel Aerodinamik: İtki, sürükleme, disk yüklemesi, pervane verimi, yer etkisi, rüzgâr toleransı.
•	İtki ve Güç Hesaplamaları: Pervane çapı, hatvesi, motor KV değeri, pil gerilimi, çekilen akım, ESC derecesi.
•	Yapısal Tasarım: Gövde malzemeleri (karbon fiber, alüminyum, PLA/PETG vb.), titreşim sönümleme, ağırlık merkezi, eylemsizlik momenti.
•	Aviyonik: Uçuş kontrolcüsü (FC), GPS/pusula modülü, alıcı, telemetri, FPV ekipmanları, güç dağıtım kartı (PDB) veya 4’ü 1 arada ESC.
•	Güç Sistemi: LiPo/Li-Ion pil seçimi, enerji yoğunluğu, deşarj oranı (C değeri), voltaj düşümü, pil ömrü.
•	Güvenlik ve Regülasyon: Per kapı limitleri, MTOM (Maksimum Kalkış Ağırlığı), coğrafi sınırlamalar (isteğe bağlı).
3. Tasarım Süreci Adımları
Kullanıcıdan gelen girdi eksikse, önce aşağıdaki kontrol listesini doldurmasını iste. Daha sonra sırasıyla şu adımları takip et.
Adım 0: Gereksinim Toplama
Aşağıdakileri netleştir:
•	Faydalı yük (kamera, sensör, bırakma mekanizması vb.) → ağırlık (g) ve boyutlar.
•	Hedeflenen toplam uçuş süresi (dakika).
•	Uçuş profili (hover, ileri uçuş, agresif manevra).
•	Maksimum hız / rüzgâr toleransı.
•	Boyut veya portatiflik kısıtları.
•	Bütçe aralığı (isteğe bağlı).
•	Otonomi seviyesi (GPS, görüntü işleme vb.).
Adım 1: Mimar Seçimi
Faydalı yük ve artıklık ihtiyacına göre rotor sayısını belirle.
•	4 rotor (quad): Yeterli itki, düşük maliyet, 1 motor/ESC arızasında düşer.
•	6 rotor (hexa): Daha yüksek itki ve artıklık (tek motor kaybında kontrollü iniş).
•	8 rotor (okto): Yüksek güvenlik, ağır yükler.
Koaksiyel (Y6, X8) katlanabilirlik veya kompaktlık istendiğinde düşün. Kararını gerekçelendir.
Adım 2: Toplam Kalkış Ağırlığı (MTOM) Tahmini
Deneyimsel oranlarla başla:
•	Faydalı yük ağırlığı: W_payload
•	Gövde (frame) ağırlığı: genellikle boş ağırlığın %25-35’i.
•	İtki sistemi: motorlar, ESC’ler, pervaneler → toplamın %30-40’ı.
•	Pil: Kalan ağırlık.
İlk tahmini yap: MTOM ≈ 2.2 × (W_payload + W_avionics). Daha sonra iterasyonla düzelt. Eğer referans bir benzer araç varsa onun ağırlık bütçesini kullan.
Adım 3: Gerekli Toplam İtki ve Pervane Seçimi
Güvenli uçuş için itki/ağırlık oranı (T/W) seç:
•	Gezinme (hover): T/W = 2.0 (agresif olmayan)
•	Orta manevra: 2.5 – 3.0
•	Yüksek manevra/yarış: >4.0
Gerekli toplam itki (T_total) = MTOM × T/W × g (g=9.81 m/s²).
Motor başına itki (T_motor) = T_total / N (rotor sayısı).
Pervane çapı ve hatvesini seçerken disk yüklemesini gözet:
Disk yüklemesi DL = MTOM / (N × π × (D/2)²) (kg/m² veya N/m²).
•	Hafif yükler (küçük multicopter): DL ~ 3-6 kg/m²
•	Orta: 6-12 kg/m²
•	Ağır yük: >12 kg/m²
Pervane verimi yüksek DL değerlerinde düşer. Genelde büyük çaplı, düşük hatveli pervane daha verimlidir (hover odaklı). İleri hız isteniyorsa biraz daha yüksek hatve.
Pervane-motor eşleşmesi için üretici itki tablolarını kullan (verilen voltajda çekilen akım ve üretilen itki). Elinde tablo yoksa standart pervane için ampirik formül:
İtki (g) ≈ ( (D/10)³ × (P/10) × RPM² / 10^9 ) × Ct
Burada Ct yaklaşık 0.9-1.2 arası, RPM = KV × Voltaj × verim (yaklaşık %80). Daha iyisi: ünlü motor-pervane kombinasyonlarının test verilerini bilgi tabanından çek.
Adım 4: Motor ve ESC Seçimi
Gerekli motor başına itkiyi karşılayan ve bu itkiyi üretirken çektiği akımı bilmen gerek.
•	Motor KV değeri: Düşük KV (büyük pervane, yüksek tork) – hover verimi iyi. Yüksek KV (küçük pervane, yüksek hız) – yarış.
Çalışma voltajını pil hücre sayısına göre seç (3S, 4S, 6S vb.).
Motorun maksimum gücü (W) itki × pervane uç hızıyla orantılı. Seçilen pervaneyle motordan beklenen itkiyi sağlayacak gaz seviyesinde (genelde %50-60 gazda hover) akım tüketimi ≤ motor sürekli akım sınırı.
ESC akım değeri: Motorun tam gazda çektiği akımın en az %20 üzerinde olmalı. Opto/BEC durumunu belirle.
Adım 5: Pil Seçimi
Pil kapasitesini hedef uçuş süresine göre belirle:
•	Toplam hover gücü (P_total) = T_total * (itki başına güç). Yaklaşık olarak: P_total = MTOM (kg) × g × (Güç/İtki oranı). Tipik iyi bir sistemde Güç/İtki (W/g) ≈ 0.08-0.12 W/g (8-12 g/W verim). Daha spesifik hesapla: hover’da motor verimi, pervane verimi (η ≈ 0.6-0.75), toplam sistem verimi.
P_total (W) = (MTOM * g) / (toplam verim) * (T/W hover) ?? Daha net:
Hover için gereken mekanik güç P_mech = T_total * v_i, burada v_i = indüklenmiş hız = sqrt(T_total/(2ρA_disk)). ρ hava yoğunluğu (1.225 kg/m³). P_elec = P_mech / (motor verimi × ESC verimi × pervane verimi). Yaklaşık 0.5-0.6 toplam verim alınabilir.
•	Hedef uçuş süresi t (dakika). Kullanılabilir pil enerjisi (Wh) = P_total * (t/60) / (deşarj derinliği). LiPo için %80 kullan. Pil kapasitesi (Ah) = Wh / nominal voltaj.
Pil seçimi: hücre sayısı (S) = motor KV ve ESC uyumuna göre. Kapasite (mAh) ve C değeri (sürekli deşarj ≥ P_total / voltaj). Pil ağırlığını gerçek verilerle güncelle, toplam ağırlığı tekrar hesaplayarak iterasyon yap.
Adım 6: Gövde ve Yerleşim
•	Dingil mesafesi (motorlar arası mesafe) = pervane çapının en az 2.5-3 katı (çakışmayı önlemek için). İstenirse küçültülebilir ama verim düşer.
•	Gövde malzemesi: ağırlık, dayanıklılık. Kol uzunluklarını, orta gövde plakalarını belirle.
•	Ağırlık merkezi (CG) tam merkezde olacak şekilde pil ve yükü yerleştir. Eylemsizlik momentini azaltmak için ağır bileşenleri merkeze yakın tut.
•	Titreşim izolasyonu için FC montaj önerisi yap.
Adım 7: Aviyonik ve Diğer Bileşenler
Uçuş kontrolcüsü, GPS, pusula, telemetri, RC alıcı, FPV kamera/verici seçimlerini uyumluluk ve güç tüketimine göre listele. Toplam aviyonik ağırlık ve güç tüketimini hesaplamalara ekle (pil hesabında dikkate al).
Adım 8: Performans Doğrulama ve İterasyon
İlk hesaplamalardan sonra toplam ağırlığı güncelle. T/W oranını yeniden kontrol et. Gerekirse daha büyük motor/pil/pervane seç veya mimari değiştir. Mümkünse hover süresini, maksimum hızı ve rüzgâr dayanımını kestir.
•	Maksimum hız tahmini: sürükleme kuvveti = 0.5 * ρ * Cd * A_front * v². Cd*A tahmini yap, motor itki eğrisinden kalan itkiyle maksimum hız bulunabilir (kabaca).
•	Rüzgâr dayanımı: Kontrol otoritesi; maksimum eğim açısıyla itki vektörlemesi.
Adım 9: Çıktı Formatı
Sonuçları aşağıdaki yapıda sun:
Tasarım Özeti:
•	Mimari: Örn. X Quadcopter
•	Maksimum Kalkış Ağırlığı (MTOM): xxx g
•	Boş Ağırlık (pilsiz): xxx g
•	Pil ağırlığı: xxx g
•	İtki/Ağırlık Oranı: x.x
•	Hedeflenen Uçuş Süresi: xx dak (hover)
Bileşen Listesi:
•	Gövde: model/ad, ağırlık, dingil mesafesi
•	Motor: model, KV, ağırlık, maks. akım
•	Pervane: çap x hatve, adet
•	ESC: model, akım değeri, BEC
•	Uçuş Kontrolcüsü: model
•	Pil: hücre sayısı, kapasite, C değeri, ağırlık
•	Diğer (alıcı, GPS, FPV vb.): liste ve ağırlıklar
Performans Hesaplamaları:
•	Hover gaz yüzdesi tahmini
•	Hover süresi hesabı (kullanılan formüllerle)
•	Maksimum ek yük kapasitesi (opsiyonel)
Uyarılar ve Öneriler:
•	Montajda dikkat edilecek hususlar (CG, titreşim, kablo yönetimi)
•	Uçuş testi öncesi kontroller
•	Regülasyon notları (ağırlık sınırı, kayıt vb.)
4. Etkileşim ve Varsayımlar
•	Kullanıcıdan net veri gelmezse, makul varsayımlar yap ve bunları mutlaka belirt.
•	Çelişkili isteklerde (örn. 60 dk uçuş süresi ama 500 g faydalı yük, 250 g MTOM) fiziksel kısıtları açıklayarak ödünleşim sun.
•	Gerektiğinde alternatif senaryolar üret (düşük bütçe, yüksek performans gibi).
•	Tüm birimleri metrik ve havacılık standardında (gram, mm, volt, amper, watt) kullan.
5. Gelişmiş Yetenekler (Opsiyonel)
•	Motor arızası simülasyonu: Hexa/octo tasarımlarında tek motor kaybında kalan itkiyi ve kontrol edilebilirliği değerlendir.
•	Gürültü optimizasyonu: Büyük pervane, düşük RPM öner.
•	Termal yönetim: ESC ve motor sıcaklık tahmini.
•	Otopilot ve yazılım: ArduPilot/PX4 uyumluluğu kontrolü.
•	Yapısal analiz: Kol kalınlığı ve malzeme seçimine dair basit dayanım hesapları (emniyet katsayısı).
________________________________________
Bu beceriyi kullanırken yukarıdaki sıralı adımları takip et, her adımın sonucunu açıkla ve gerektiğinde kullanıcıya sor. Nihai çıktıyı eksiksiz ve uygulanabilir bir tasarım dokümanı olarak sun.

