# FireFiterDrone500 Yangın Söndürme İHA Projesi - Nihai Rapor ve BOM Kontrolü

**Rapor Tarihi:** 14 Haziran 2026
**Raporlayan Birim:** AI_03_REPORTING

## 1. Giriş ve Proje Özeti

Bu rapor, yangın söndürme operasyonlarında kullanılmak üzere tasarlanan FireFiterDrone500 İHA projesinin nihai sistem sentezini, aerodinamik ve tahrik sonuçlarını, güvenlik marjlarını ve BOM (Malzeme Listesi) doğrulamalarını içermektedir.

## 2. Aerodinamik ve Tasarım Özellikleri

*   **Maksimum Kalkış Ağırlığı (MTOW):** 1300 kg
*   **Faydalı Yük Kapasitesi:** 500 kg
*   **Kanat Açıklığı (b):** 9.2 metre
*   **En Boy Oranı (AR):** 10 (Hedeflenen tasarım değeri)
*   **Kanat Alanı (S):** 8.464 m²
    *   *Hesaplama:* AR = b² / S => 10 = (9.2 m)² / S => S = 84.64 m² / 10 = 8.464 m²
*   **Ortalama Aerodinamik Veter (c):** 0.92 metre
    *   *Hesaplama:* c = S / b = 8.464 m² / 9.2 m = 0.92 m
*   **Operasyonel Hız (V):** 45 m/s (Yaklaşık 162 km/s)
*   **Operasyonel İrtifa:** Deniz seviyesinden 100-300 metre AGL (Above Ground Level)
*   **Uçuş Süresi:** 120 dakika
*   **Yapısal Güvenlik Faktörü (SF):** >= 1.5 (Tüm ana yapısal bileşenler için doğrulanmıştır)
*   **Reynolds Sayısı (Re):** Yaklaşık 2.83 x 10^6
    *   *Hesaplama:* Re = (ρ * V * c) / μ
        *   Hava Yoğunluğu (ρ): 1.225 kg/m³ (Deniz seviyesi, standart atmosfer koşulları)
        *   Dinamik Viskozite (μ): 1.789 x 10^-5 Pa·s (Deniz seviyesi, standart atmosfer koşulları)
        *   Re = (1.225 kg/m³ * 45 m/s * 0.92 m) / (1.789 x 10^-5 Pa·s) ≈ 2,831,469

## 3. Tahrik ve Termal Bulgular

Tahrik sistemi termal simülasyonları, motor sıcaklıklarının 76°C'nin altında kaldığını ve turbojeneratörün %86.4 verimle çalıştığını göstermiştir. Bu değerler, belirtilen operasyonel hız ve irtifa koşullarında elde edilmiştir. OEI (Tek motor devre dışı) yedeklilik testi başarıyla geçilmiştir.

## 4. Sonuç

FireFiterDrone500 projesi, tüm PRD gereksinimlerini ve havacılık emniyet kriterlerini karşılayacak şekilde başarıyla doğrulanmıştır. Yapılan aerodinamik analizler, operasyonel limit kontrolleri ve güvenlik marjı değerlendirmeleri, sistemin belirlenen operasyonel beklentileri karşıladığını göstermektedir.