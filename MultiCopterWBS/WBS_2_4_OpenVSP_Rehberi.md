# 🖥️ WBS 2.4 — OpenVSP 3D MODEL OLUŞTURMA

> **mc.vsp3 Dosyası | Pod + Disk + Kol + Rotor Bileşenleri | CG Konumu**  
> OpenVSP NASA v3.36 | NDARC §5 | CadQuery Ek Model | Pydantic VSPResult

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 2.4 |
| **Faz** | AŞAMA 2 — Konfigürasyon & 3D Geometri |
| **Görev** | OpenVSP Parametrik 3D Model Oluşturma |
| **Girdi** | `geometry.json` (WBS 2.2) + `yaw_balance.json` (WBS 2.3) + `mass_budget.json` (WBS 1.4) |
| **LLM Script** | `vsp_build.py` |
| **Çıktı** | `mc.vsp3`, `mc.stl`, `vsp_model.json`: component_list[], CG_m[], disk_area_m2, wetted_area_m2, bounding_box_m[] |
| **Kabul Kriteri** | mc.vsp3 hatasız açılır \| n_disk = n_rotors \| \|CG_z\| ≤ 0.05 m \| Pydantic PASS |
| **Sonraki WBS** | WBS 2.5 Kol & Hub CadQuery \| WBS 2.6 CG Doğrulama \| WBS 5.1 CFD Hazırlığı |
| **Standartlar** | OpenVSP NASA v3.36 \| NDARC §5 \| OpenVSP User Manual §4 \| MIL-STD-31000B |

---

## 🔟 5 Adımlı Algoritma

### Adım 1: OpenVSP Kurulumu

```python
import openvsp as vsp
vsp.ClearVSPModel()
vsp.SetVSPAERODefaultSettings()
# Birim: SI (metre) | Koordinat: X=ileri, Y=sağ, Z=yukarı
# Gerekli sürüm: OpenVSP ≥ v3.30 (Python API)
```

### Adım 2: Merkez Hub (POD)

```python
hub_id = vsp.AddGeom('POD')
vsp.SetParmVal(hub_id, 'Length',    'Design', hub_diam * 2.0)
vsp.SetParmVal(hub_id, 'FineRatio', 'Design', 2.0)
# Konum: [0, 0, 0] — CG referans noktası
```

### Adım 3: Kollar (FUSELAGE)

```python
for i in range(n_arms):
    phi_deg = i * 360.0 / n_arms
    arm_id = vsp.AddGeom('FUSELAGE')
    vsp.SetParmVal(arm_id, 'Length',            'Design', arm_length_m)
    vsp.SetParmVal(arm_id, 'Z_Rel_Rotation',    'XForm',  phi_deg)
    vsp.SetParmVal(arm_id, 'Y_Rel_Rotation',    'XForm',  90.0)
```

### Adım 4: Rotor Diskleri (PROP)

```python
for i, pos in enumerate(motor_positions_m):
    disk_id = vsp.AddGeom('PROP')
    vsp.SetParmVal(disk_id, 'Diameter',   'Design', D_rotor_m)
    vsp.SetParmVal(disk_id, 'NumBlade',   'Design', 2)        # sembolik
    vsp.SetParmVal(disk_id, 'X_Location', 'XForm',  pos[0])
    vsp.SetParmVal(disk_id, 'Y_Location', 'XForm',  pos[1])
    vsp.SetParmVal(disk_id, 'Z_Location', 'XForm',  pos[2])
    # Coaxial: üst z=+0.05 m, alt z=-0.05 m
```

### Adım 5: CG Hesabı & Kayıt

```python
CG_x = sum(m_i * x_i) / m_total
CG_y = sum(m_i * y_i) / m_total
CG_z = sum(m_i * z_i) / m_total
# Kabul: |CG_z| ≤ 0.05 m

vsp.WriteVSPFile('mc.vsp3')
vsp.ExportFile('mc.stl', SET_ALL, EXPORT_STL)
```

---

## 🧩 OpenVSP Bileşen Kataloğu

| Bileşen | API | Kullanım | Adet (n=6) |
|---------|-----|----------|------------|
| **POD** | `AddGeom('POD')` | Merkez hub gövdesi | 1 |
| **FUSELAGE** | `AddGeom('FUSELAGE')` | Kollar (her kol = 1) | 6 |
| **PROP** | `AddGeom('PROP')` | Rotor disk alanı | 6 |
| **WING** | `AddGeom('WING')` | Tilt-prop kanat | 0 (çoğu) |
| **POINT MASS** | `AddMass()` | Batarya, payload, aviyonik | 3–6 |

---

## 📐 CG Bileşen Matrisi

| Bileşen | Fraksiyon | z_i (tipik) | Not |
|---------|-----------|-------------|-----|
| Hub (gövde+aviyonik) | 0.06 | 0 | Referans nokta |
| Kollar (×n) | 0.08 | 0 | Eşit dağılım → CG_x,y ≈ 0 |
| Motorlar (×n) | 0.10 | 0 | Eşit dağılım |
| Rotorlar (×n) | 0.05 | +0.02 m | Üstte |
| Batarya | 0.35 | −0.05 m | Altta yerleştir |
| Güç elektroniği | 0.05 | ±Δz | Ayarlanabilir |
| Aviyonik | 0.03 | 0 | Merkeze yakın |
| Payload | ≥0.15 | −0.10 m | Altta merkezi |
| Misc | 0.02 | 0 | — |

**CG Kabul Kriterleri:**
- `|CG_x| ≤ 0.01 m` — ön/arka denge
- `|CG_y| ≤ 0.01 m` — sol/sağ denge
- `|CG_z| ≤ 0.05 m` — düşey sapma (KK-7 hazırlık)
- Payload değişiminde CM kayması ≤ 3 mm (KK-6)

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| — | n_disk | = n_rotors | Disk ekleme scriptini kontrol et |
| KK-7 hazırlık | \|CG_z\| | ≤ 0.05 m | Batarya/payload konumunu ayarla |
| — | mc.vsp3 | Hatasız açılır | VSP API hata logunu incele |
| — | Pydantic | PASS | VSPResult validator hatasını düzelt |

---

## 🔗 WBS Bağlantıları

```
geometry.json (WBS 2.2)    ──┐
yaw_balance.json (WBS 2.3) ──┤── vsp_build.py ──► mc.vsp3
mass_budget.json (WBS 1.4) ──┘         │           vsp_model.json
                                        ├── WBS 2.5 arm_cad.py (CadQuery detay)
                                        ├── WBS 2.6 cg_verify.py
                                        ├── WBS 5.1 vspaero_run.py (CFD)
                                        └── WBS 14.3 görsel dokümantasyon (STL)
```

---

## vsp_model.json Şeması (Pydantic VSPResult)

```python
class VSPResult(BaseModel):
    n_rotors:          int
    layout:            str
    component_list:    List[dict]     # tip, id, isim, konum
    CG_m:              List[float]    # [x, y, z] metre
    disk_area_m2:      float          # gt=0
    wetted_area_m2:    float          # ge=0
    bounding_box_m:    List[float]    # [xmin,xmax,ymin,ymax,zmin,zmax]
    vsp_file:          str            # 'mc.vsp3'
    n_disk_check:      bool           # n_disk == n_rotors
    CG_z_ok:           bool           # |CG_z| ≤ 0.05 m
    validation_passed: bool = True
```

---

*WBS 2.4 OpenVSP 3D Model Oluşturma Detay Rehberi v4.0 — Nisan 2026*  
*5 Adım | POD+FUSELAGE+PROP | CG Matrisi | Pydantic VSPResult | mc.vsp3 + mc.stl*
