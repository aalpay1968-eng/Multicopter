# 🚁 FFD500 Orkestra Protokolü

## 1. Amaç
Bu protokol, FireFiterDrone500 projesinde görev alan tüm AI ajanlarının koordineli, tutarlı ve hatasız çalışmasını sağlar.

## 2. Temel İlkeler (ZERO TOLERANCE POLICY)
- **Doğruluk:** Tüm teknik veriler kaynak gösterilmeli veya hesaplanmalıdır. Tahmini bilgi yasaktır.
- **Şeffaflık:** Her kararın arkasındaki mantık belgelenmelidir.
- **Çapraz Doğrulama:** Kritik çıktılar en az bir başka ajan tarafından kontrol edilmelidir.
- **Versiyon Kontrolü:** Tüm değişiklikler Git üzerinden izlenmelidir.

## 3. İletişim Mekanizması
- **Durum Dosyası:** `ORCHESTRA_STATE.json` (Anlık görev dağılımı)
- **Log Dosyası:** `ORCHESTRA_LOG.md` (Ajanlar arası asenkron iletişim)
- **Raporlama:** Her ajan 30 dakikada bir ilerleme raporu vermelidir.

## 4. Görev Yaşam Döngüsü
1. **Atama:** `ORCHESTRA_STATE.json` dosyasına görev eklenir.
2. **Başlangıç:** Ajan durumu "IN_PROGRESS" yapar.
3. **Çıktı:** İlgili klasöre dosyalar kaydedilir.
4. **Doğrulama:** QA ajanı çıktıyı kontrol eder.
5. **Tamamlanma:** Durum "COMPLETED" yapılır ve log güncellenir.

## 5. Klasör Yapısı
- `/docs`: Protokoller ve durum dosyaları
- `/reports`: Mühendislik raporları
- `/manufacturing`: BOM ve üretim çizimleri
- `/cad`: 3D model dosyaları (OpenSCAD, STL)
- `/software`: Uçuş yazılımı ve ajan kodları
- `/electronics`: PCB şemaları ve yerleşim

---
*Son Güncelleme: 2026-06-08 | Orkestra Şefi: Qwen*
