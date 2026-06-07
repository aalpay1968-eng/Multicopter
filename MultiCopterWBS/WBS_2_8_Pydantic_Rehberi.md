# ✅ WBS 2.8 — OpenVSP PYDANTIC ÇIKTI STANDARDİZASYONU

> **WBS 2.1–2.7 Tüm Çıktılarını Birleştir | phase_2_geometry.json | Tam Doğrulama**  
> Pydantic v2 | JARUS SORA OSO#07 | EASA SC-VTOL §2510 | AŞAMA 2 KAPANIŞI

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 2.8 |
| **Faz** | AŞAMA 2 — Konfigürasyon & 3D Geometri  |  **AŞAMA 2 KAPANIŞ** |
| **Görev** | OpenVSP Pydantic Çıktı Standardizasyonu |
| **Girdi** | `config.json` (2.1) + `geometry.json` (2.2) + `yaw_balance.json` (2.3) + `vsp_model.json` (2.4) + `cad_model.json` (2.5) + `cg_result.json` (2.6) + `landing_gear.json` (2.7) |
| **LLM Script** | `parse_vsp_mc.py` |
| **Çıktı** | `phase_2_geometry.json`: tüm WBS 2.x alanları + validation_passed + kk_summary{} + wbs_checklist{} |
| **Kabul Kriteri** | validation_passed = True \| yaw_balanced = True \| Tüm zorunlu alanlar dolu \| Tüm KK PASS \| AŞAMA 3 geçişi onaylandı |
| **Sonraki WBS** | WBS 3.1 Disk Loading \| WBS 7.1 6-DOF \| JARUS SORA OSO#07 kanıtı |
| **Standartlar** | Pydantic v2 \| JARUS SORA v2.5 OSO#07 \| EASA SC-VTOL §2510 \| DO-178C §6.3 |

---

## 🏗️ WBS 2.8'in Rolü

```
WBS 2.1 config.json        ──┐
WBS 2.2 geometry.json      ──┤
WBS 2.3 yaw_balance.json   ──┤
WBS 2.4 vsp_model.json     ──┤──► parse_vsp_mc.py ──► phase_2_geometry.json
WBS 2.5 cad_model.json     ──┤                              │
WBS 2.6 cg_result.json     ──┤                    validation_passed = True?
WBS 2.7 landing_gear.json  ──┘                              │
                                               YES: AŞAMA 3'e geç ✅
                                               NO:  İlgili WBS'e geri dön ❌
```

---

## 🔑 KK-1..KK-13 Kontrol Matrisi (AŞAMA 2 Kapanışı)

| KK | Parametre | Limit | Kaynak | AŞAMA 3 Etkisi |
|----|-----------|-------|--------|----------------|
| **KK-2** | T/W @ OEI | ≥ 1.0 | config.json | BLOKE |
| **KK-4** | DL_actual | ≤ 300 N/m² | geometry.json | BLOKE |
| **KK-6** | EI_ok + payload_CG | True + ≤ 3mm | cad + cg | BLOKE |
| **KK-7** | CG sapma x,y,z | ≤10/10/50 mm | cg_result.json | BLOKE |
| **KK-8** | s/D_ratio | ≥ 1.10 | geometry.json | BLOKE |
| **KK-10** | Devrilme açısı | ≥ 30° | landing_gear.json | BLOKE |
| **KK-13** | Yaw imbalance | ≤ 0.01 N·m | yaw_balance.json | BLOKE |
| KK-1 | T/W @ hover | ≥ 2.0 | WBS 3.1'de onay | Uyarı |
| KK-5 | FM | ≥ 0.60 | WBS 3.2'de onay | Uyarı |
| KK-9 | Aviyonik BW | ≥ 10 Hz | WBS 8'de onay | Bekliyor |

---

## 📐 Unified GeometryPhase2 Şeması

```python
class GeometryPhase2(BaseModel):
    config:   ConfigSection        # WBS 2.1: n_rotors, layout, rotation_dirs, OEI_OK
    geometry: GeometrySection      # WBS 2.2: D_rotor, WB, s/D, DL, motor_positions
    yaw:      YawSection           # WBS 2.3: Q_yaw, rank_B, cond_B
    vsp:      VSPSection           # WBS 2.4: mc.vsp3, disk_area, CG_m
    cad:      CADSection           # WBS 2.5: D_out, EI_ok, m_arm
    cg:       CGSection            # WBS 2.6: CG_x/y/z, KK7, SM%, payload_CG_ok
    landing:  LandingSection       # WBS 2.7: KK10, tipover, clearance_ok
    # Meta alanlar
    validation_passed: bool = True
    phase_2_complete:  bool = True
    wbs_version:       str  = "v4.0"
    kk_summary:        Dict[str, str]    # {'KK-2':'PASS', 'KK-4':'PASS', ...}
```

**Sub-model validator'lar (seçkiler):**

```python
# ConfigSection:
rotation_dirs: count('CW') == count('CCW')   # KK-13 sayısal

# GeometrySection:
s_D_ratio >= 1.10      # KK-8
DL_actual_Nm2 <= 300   # KK-4

# YawSection:
|Q_yaw_imbalance| <= 0.01 N·m   # KK-13
rank_B == 4

# CGSection:
KK7_all_pass == True   # |CG_x|≤10mm, |CG_y|≤10mm, |CG_z|≤50mm
SM_percent >= 5.0
payload_CG_ok == True  # ≤ 3mm kayma (KK-6)

# LandingSection:
tipover_angle_deg >= 30.0   # KK-10
```

---

## 📋 Zorunlu Alan Özeti (30 alan)

| WBS | JSON | Zorunlu Alan Sayısı | Kritik Validator |
|-----|------|---------------------|-----------------|
| 2.1 | config.json | 7 | OEI_OK, rotation_dirs CW=CCW |
| 2.2 | geometry.json | 8 | DL≤300, s/D≥1.10 |
| 2.3 | yaw_balance.json | 4 | \|Q_yaw\|≤0.01, rank=4 |
| 2.4 | vsp_model.json | 4 | n_disk_check=True |
| 2.5 | cad_model.json | 4 | EI_ok=True |
| 2.6 | cg_result.json | 6 | KK7_all_pass, SM≥5% |
| 2.7 | landing_gear.json | 4 | tipover≥30°, clearance_ok |
| 2.8 meta | — | 4 | validation_passed, phase_2_complete |

---

## ⚠️ Hata Yönetimi

```python
try:
    result = GeometryPhase2(...)
    # Tüm validatorlar PASS → phase_2_geometry.json yaz
except ValidationError as e:
    # Hangi alan hangi WBS'e ait? → escalation_report.json
    for err in e.errors():
        loc   = err['loc']     # örn: ('cg', 'KK7_all_pass')
        msg   = err['msg']
        wbs   = field_to_wbs[loc[0]]  # {'cg':'WBS 2.6', ...}
        print(f'[{wbs}] {loc}: {msg}')
    raise SystemExit('AŞAMA 2 KAPANMADI — ilgili WBS düzelt ve tekrar çalıştır')
```

---

## 🔗 JARUS SORA OSO#07 Bağlantısı

`phase_2_geometry.json` → **OSO#07: UAS konfigürasyon uyumu kontrol edilmiş** kanıtı  
`kk_summary{}` → tüm KK geçiş kayıtları traceability için saklanır  
`wbs_version: v4.0` → konfigürasyon yönetim referansı (CM baseline)

---

*WBS 2.8 Pydantic Çıktı Standardizasyonu Detay Rehberi v4.0 — Nisan 2026*  
*AŞAMA 2 KAPANIŞI | 7 JSON → 1 Unified Schema | KK-2/4/6/7/8/10/13 | Pydantic GeometryPhase2*
