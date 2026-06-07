# 🔩 WBS 2.5 — KOL & HUB CAD MODELİ (CadQuery)

> **Kol Tüp Boyutları | Hub Şekli | Flanş & Menteşe | STEP & STL Export**  
> CadQuery 2.x API | MIL-STD-31000B | ISO 2768-m | WBS 6.1 FEA Hazırlığı

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 2.5 |
| **Faz** | AŞAMA 2 — Konfigürasyon & 3D Geometri |
| **Görev** | Kol & Hub Parametrik CAD Modeli |
| **Girdi** | `geometry.json` (WBS 2.2) + `config.json` (WBS 2.1) + `vsp_model.json` (WBS 2.4) |
| **LLM Script** | `arm_cad.py` |
| **Çıktı** | `arm_tube.step`, `hub_body.step`, `motor_flange.step`, `assembly.step`, `cad_model.json` |
| **Kabul Kriteri** | STEP hatasız açılır \| EI_actual ≥ EI_min \| hinge_bolt ≥ 2 (katlanır) \| Pydantic PASS |
| **Sonraki WBS** | WBS 2.6 CG Doğrulama \| WBS 6.1 FEA \| WBS 12.2 Montaj \| WBS 14.3 Teknik Çizim |
| **Standartlar** | CadQuery 2.x \| MIL-STD-31000B \| ISO 2768-m \| MIL-HDBK-5J \| ASME B31.3 |

---

## 🔟 5 Adımlı Algoritma

### Adım 1: Kol Tüp Kesit Boyutu

```python
D_out  = max(0.016, D_rotor * 0.08)   # m; CFRP
t_wall = max(0.001, D_out * 0.10)     # m
D_in   = D_out - 2 * t_wall

I = pi/64 * (D_out^4 - D_in^4)
EI_actual = E_CFRP * I              # E_CFRP = 70 GPa

# EI_min kontrolü (WBS 6.1 ön):
F_tip     = m_motor * g * 3.5       # 3.5g tasarım yükü
EI_min    = F_tip * L_arm^3 / (3 * L_arm * 0.01)
assert EI_actual >= EI_min
```

**Kesit Seçim Tablosu:**

| Konfigürasyon | D_rotor | D_out | t_wall | Malzeme | EI (N·m²) |
|---------------|---------|-------|--------|---------|-----------|
| Quad-X küçük | 0.15 m | 16 mm | 1.6 mm | CFRP T700 | 8.2 |
| Hex-X kargo | 0.38 m | 25 mm | 2.5 mm | CFRP T700 | 52 |
| Octo-X8 ağır | 0.55 m | 35 mm | 3.5 mm | CFRP T700 | 198 |
| X-12 endüstri | 0.65 m | 40 mm | 4.0 mm | CFRP T700 | 329 |
| X-16 büyük | 0.90 m | 60 mm | 5.0 mm | CFRP T300 | 1520 |
| Hex-X Al | 0.38 m | 30 mm | 3.0 mm | Al 6061-T6 | 107 |

### Adım 2: Hub Gövde Modeli

```python
hub = (cq.Workplane("XY")
    .circle(hub_diam/2 * 1000)          # dış çap (mm)
    .circle((hub_diam - 2*t_hub)/2 * 1000)  # iç çap
    .extrude(L_hub * 1000))
# Hub şekli: CYLINDER | HEXAGONAL (n=6) | OCTAGONAL (n=8)
# socket_depth = D_out * 4.0  (kol priz yuva derinliği)
```

### Adım 3: Motor Flanşı

```python
OD_flange = stator_diam * 1.3
bc        = OD_flange * 0.75          # bolt circle çapı
# 4 x M4 delik @ 90° aralıklı
# Sıkma momenti: M4 → 1.5 N·m (Loctite 243)
```

### Adım 4: Katlanır Kol Menteşesi (Koşullu)

Sadece `arm_fold_flag = True` iken uygulanır.

| Parametre | SINGLE_AXIS | DUAL_AXIS | SNAP_LOCK |
|-----------|-------------|-----------|-----------|
| Katlanma açısı | 90° | 90/180° | 90° |
| Cıvata | 4 × M5 | 4 × M5 | 3 × M5 |
| Kütle eki | +%5 kol | +%8 kol | +%4 kol |
| TBO | 500 katlanma | 300 katlanma | 1000 katlanma |
| Tolerans | H7/h6 | H7/h6 | H8/f7 |

> **Kural:** `hinge_bolt_count ≥ 2` — aksi halde Pydantic validator reddeder.

### Adım 5: CAD Export & Doğrulama

```python
cq.exporters.export(arm_solid,    'arm_tube.step')
cq.exporters.export(hub_solid,    'hub_body.step')
cq.exporters.export(flange_solid, 'motor_flange.step')
cq.exporters.export(arm_solid,    'arm_tube.stl')

# Doğrulama:
assert solid.isValid()      # geometri bütünlüğü
assert solid.Volume() > 0   # kapalı katı
```

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| — | EI_actual | ≥ EI_min | D_out artır veya t_wall artır |
| — | hinge_bolt | ≥ 2 (katlanırsa) | Menteşe cıvata sayısını artır |
| — | solid.isValid() | True | CadQuery geometriyi kontrol et |
| — | STEP export | Hatasız | CadQuery sürümünü kontrol et |
| MS ≥ 1.5 | (WBS 6.1'de) | ≥ 1.5 | Kesit boyutunu büyüt |

---

## 🔗 WBS Bağlantıları

```
geometry.json (WBS 2.2)  ──┐
config.json (WBS 2.1)    ──┤── arm_cad.py ──► arm_tube.step
vsp_model.json (WBS 2.4) ──┘                  hub_body.step
                                               cad_model.json
                                    │
                    ┌───────────────┼──────────────┐
                    ▼               ▼              ▼
            WBS 2.6 cg_verify  WBS 6.1 FEA   WBS 14.3 teknik çizim
            (m_arm güncelle)  (arm_tube.step) (DXF üretimi)
```

---

## cad_model.json Şeması (Pydantic CADResult)

```python
class CADResult(BaseModel):
    n_arms:             int
    layout:             str
    D_out_m:            float    # gt=0
    t_wall_m:           float    # gt=0
    D_in_m:             float    # gt=0
    EI_actual_Nm2:      float    # gt=0
    EI_min_Nm2:         float    # gt=0
    EI_ok:              bool     # EI_actual >= EI_min
    m_arm_single_kg:    float    # gt=0
    hub_diam_m:         float    # gt=0
    socket_depth_m:     float    # gt=0
    arm_fold_flag:      bool
    hinge_bolt_count:   int      # >= 2 if fold
    export_files:       List[str]
    cad_valid:          bool
    validation_passed:  bool = True
```

---

*WBS 2.5 Kol & Hub CAD Modeli Detay Rehberi v4.0 — Nisan 2026*  
*5 Adım | CadQuery 2.x OCCT | STEP+STL Export | EI Kontrolü | Pydantic CADResult*
