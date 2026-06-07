# AI Orkestra Görev Dağıtımı (ORKESTRA_GOREV_DAGITIMI.md)

Bu dosya, Orkestra Şefi ve Ajanlar arasında koordinasyonu ve iş bölümünü sağlar.

## Ajan: Qwen Coder (Optimizasyon Ajanı)
**Görev:** Multicopter konfigürasyonunu optimize etmek.
**Hedefler:**
1. **Faydalı Yük Oranı**: 50 kg faydalı yük taşıyan drone için MTOW'un 135 kg olması durumunda, motor gücü ve rotor alanlarını optimize ederek toplam itki marjını artırın.
2. **Coaxial Kayıplar**: Coaxial tasarımda (X4-coax, 8 rotor) üst ve alt rotorlar arasındaki girişim kayıplarını en aza indirmek için rotor çapını ve eksenler arası dikey mesafeyi (Z mesafesi) optimize edin.
3. **Kütle Bütçesi**: Boş ağırlığı minimize edin.
4. **Git İşlemleri**: Yapılandırılan optimizasyonları config.json ve geometry.json dosyalarına kaydederek agent/qwen_coder/20260607_optimization branch'inde commit edin ve push edin.
