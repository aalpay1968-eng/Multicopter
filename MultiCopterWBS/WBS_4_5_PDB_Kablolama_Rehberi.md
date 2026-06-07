# ⚙️ WBS 4.5 v1.0 — GÜÇ DAĞITIM KARTI (PDB) & KABLOLAMA

> **I_PDB Boyutlandırma | AWG Hesabı | BEC 5V/12V | Sigorta | DO-160G §16**

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 4.5 v1.0 |
| **Bağımlılık** | WBS 3.9 thrust_chain.json + WBS 4.4 bms.json |
| **Çıktı** | pdb.json |
| **Standart** | IEC 60364-7-712 | DO-160G §16 | MIL-W-22759 |

---

## 🔟 5 Adımlı Algoritma

### Adım 2: PDB Akımı

```python
I_avionics   = avionics_power_W / V_bat_nom
I_PDB        = I_total + I_avionics
I_PDB_rated  = I_PDB * 1.30      # güvenlik faktörü ≥ 1.30
I_fuse       = I_PDB_rated * 1.10
```

### Adım 3: AWG Kablo Seçimi

```python
J_MAX = 3.0  # A/mm² — havacılık standardı (MIL-W-22759)

A_mm2_req = I_PDB_rated / J_MAX
# AWG tablosundan en yakın standart değer seçilir
# V_drop = I × R_kablo ≤ 0.5V (1m kablo)
```

---

## 📊 AWG Referans Tablosu

| AWG | mm² | I_max sürekli | I_max anlık | UAV Kullanım |
|-----|-----|--------------|------------|-------------|
| **AWG 8** | 8.37 | 50 A | 80 A | Ana güç (>40A) |
| **AWG 10** | 5.26 | 30 A | 50 A | Ana hat (20-40A) |
| AWG 12 | 3.31 | 20 A | 35 A | Motor hatları |
| AWG 14 | 2.08 | 13 A | 22 A | ESC çıkışı |
| AWG 16 | 1.31 | 8 A | 14 A | BEC çıkışı |
| AWG 18 | 0.82 | 5 A | 9 A | FCU/GPS beslemesi |
| AWG 20 | 0.52 | 3 A | 6 A | RC/Telemetri |

---

## 🔌 Konektör Kataloğu

| Tip | I_max | V_max | UAV Kullanım |
|-----|-------|-------|-------------|
| **XT90** | 90 A | 60 V | Ana batarya — standart |
| **AS150** | 150 A | 60 V | Ağır platform; anti-spark |
| XT60 | 60 A | 60 V | Orta platform (6S/8S) |
| EC5 | 120 A | 80 V | Askeri/endüstriyel |

---

## ✅ Kabul Kriterleri

| Kriter | Limit | İhlal Eylemi |
|--------|-------|--------------|
| I_PDB_rated | ≥ I_total × 1.30 | PDB boyutunu artır |
| J_max | ≤ 3 A/mm² | Kalın AWG seç |
| V_drop | ≤ 0.5V | AWG bir boy büyüt |
| BEC_5V | ≥ 3A | Daha güçlü BEC |
| Sigorta | I_fuse = I_PDB × 1.10 | Standart sigorta değeri |

---

## PDBResult Şeması

```python
class PDBResult(BaseModel):
    I_motor_A:    float
    I_avionics_A: float
    I_PDB_total:  float
    I_PDB_rated:  float
    I_fuse_A:     float
    AWG_main:     int
    AWG_motor:    int
    V_drop_V:     float
    BEC_5V_A:     float
    BEC_12V_A:    float
    weight_g:     int
    J_check:      bool
    validation_passed: bool = True
```

---

*WBS 4.5 v1.0 — Mayıs 2026 | AWG + Sigorta + BEC | DO-160G §16 | J_max ≤ 3 A/mm²*
