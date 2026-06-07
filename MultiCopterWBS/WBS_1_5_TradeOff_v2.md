# 🔀 WBS 1.5 v2 — KAPSAMLI TRADE-OFF ANALİZİ (0–5000 kg)

> **16 alternatif konfigürasyon | 7 payload sınıfı | 0–5000 kg spektrum**
> Ağırlıklı Pugh Matrisi | Payload filtresi | Sertifikasyon yolları

---
## 📦 7 Payload Sınıfı & Önerilen Konfigürasyon

| Sınıf | Payload | Önerilen | OEI | Güç | Sertifikasyon |
|-------|---------|----------|-----|-----|---------------|
| 1 | 0–1 kg | **A1 Quad-X** | — | — | Hafif, basit, hobi/hafif gözetleme |
| 1 | 1–3 kg | **A2 Hex-X** | — | — | N+1 güvenlik + BVLOS uyumu |
| 2 | 3–15 kg | **A3 Octo-X8** | — | — | N+2 OEI, yüksek payload |
| 3 | 15–50 kg | **A5/A6 Dodeca/CoaxHex** | — | — | N+2/N+3, endüstriyel (GRIFF 300 ref.) |
| 4 | 50–150 kg | **A9 DEP-18rot** | — | — | N+6+ redundancy, şehir içi eVTOL |
| 5 | 150–500 kg | **A10 Tilt-Prop Hibrit** | — | — | Uzun menzil + VTOL, tilt-wing |
| 6 | 500–2000 kg | **A12 Tandem-Coaxial** | — | — | Büyük disk FM, kanıtlanmış teknoloji |
| 7 | 2000–5000 kg | **A14/A16 Hibrit/Turboshaft** | — | — | CS-29 sertifikalı, max payload |

---
## 🚁 16 Alternatif Özet

| ID | Konfigürasyon | Payload Max | N | OEI | Referans |
|----|---------------|------------|---|-----|---------|
| **A1** | Quadcopter-X (4 rotor) | 0–3 kg | 4 | Yok | DJI Mini 4 Pro, Mavic 3 Enterprise |
| **A2** | Hexacopter-X (6 rotor) | 0.5–4 kg | 6 | N+1 | DJI Matrice 300, Freefly Alta X |
| **A3** | Octocopter-X8 flat (8 rotor) | 3–15 kg | 8 | N+2 | GRIFF 135, Freefly Alta 8, T-Drones M120 |
| **A4** | Y6 Coaxial Tricopter | 2–8 kg | 6 | Koşullu N+1 | 3DR Y6, özel tasarımlar |
| **A5** | Dodecacopter-X (12 rotor flat) | 15–50 kg | 12 | N+3 | SPH Engineering Spider-120, özel endüstr |
| **A6** | Coaxial Hexacopter-12 (6 kol × 2) | 12–45 kg | 12 | N+2 | GRIFF 300 (225kg payload, EASA sertifika |
| **A7** | Hexadecacopter-X (16 rotor flat) | 25–80 kg | 16 | N+4 | Volocopter VoloDrone (200 kg payload, 18 |
| **A8** | Tandem Rotor (2 büyük rotor — helikopter benzeri) | 50–200 kg | 2 | N+1 (sınırlı) | Boeing MH-6, Kaman K-MAX (insansız kargo |
| **A9** | Dağıtık Elektrik Propülsiyon DEP (18-24 küçük rotor) | 40–120 kg | 18 | N+6+ | Joby S4, Lilium Jet konsept, NASA X-57 M |
| **A10** | eVTOL Tilt-Prop Hibrit (kanat + VTOL rotorları) | 100–400 kg | 8 | N+2 | Pipistrel Nuuva V300 (300 kg payload), B |
| **A11** | Büyük Coaxial Octocopter (4 çift rotor → X8 büyük ölçek) | 150–600 kg | 8 | N+2 | GRIFF 300 büyük versiyonu (225 kg), Boei |
| **A12** | Büyük Disk Tandem Coaxial (2 büyük koaxial rotor sistemi) | 400–1500 kg | 4 | N+1 | Kaman K-MAX (insansız): 2700 kg MTOW, 13 |
| **A13** | Yüksek Kapasiteli DEP eVTOL (32+ rotor modüler) | 600–2000 kg | 32 | N+8+ | Volocopter VoloFreighter konsept (2000 k |
| **A14** | Hibrit Türbin-Elektrik VTOL Kargo (insanlı türev tabanlı) | 1500–5000 kg | 8 | N+2 | Bell 525 Relentless tabanlı, Sikorsky CH |
| **A15** | Sertifikalı İnsanlı Sınıfı eVTOL (CS-23/SC-VTOL Certified) | 500–4000 kg
(yolcu+bagaj dahil) | 12 | N+2 (CS-29 §29.1309) | EHang 216-S (CAAC TC; 240 kg MTOW, ~100  |
| **A16** | Yanıcı Yakıt Büyük Multirotor (ICE / Turboshaft güdümlü) | 2000–8000 kg | 8 | N+1 | Mil Mi-26 insansız türev konsept (20t MT |

---
## 🐍 Payload Filtreli Seçim Akışı
```python
cls_num, candidates = get_payload_class(payload_kg)  # Sınıf belirle
eliminate_BVLOS(candidates)     # OEI gereksinimi
eliminate_SAIL(candidates)       # Sertifikasyon uyumu
eliminate_payload_cap(candidates)# Max payload kontrolü
winner = pugh_weighted(candidates)  # En iyi skor
```

---
*WBS 1.5 v2 — 0–5000 kg Payload Spektrumu | Nisan 2026*