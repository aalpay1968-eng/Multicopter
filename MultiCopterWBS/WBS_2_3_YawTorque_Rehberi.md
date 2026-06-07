# 🔄 WBS 2.3 — YAW TORQUE DENGESİ

> **Q_drag Hesabı | Σ(CW−CCW) İmbalance | Mixing Matrix Ön Kontrolü**  
> Prouty §4 | Mahony 2012 | PX4 Mixer | KK-13: |Q_yaw| ≤ 0.01 N·m

---

## 📍 Genel Bakış

| Alan | Değer |
|------|-------|
| **WBS Kodu** | WBS 2.3 |
| **Faz** | AŞAMA 2 — Konfigürasyon & 3D Geometri |
| **Görev** | Yaw Torque Dengesi Doğrulama |
| **Girdi** | `config.json` (WBS 2.1) + `geometry.json` (WBS 2.2) + `bemt.json` (WBS 3.2, opsiyonel) |
| **LLM Script** | `yaw_balance.py` |
| **Çıktı** | `yaw_balance.json`: Q_per_rotor[], Q_yaw_imbalance_Nm, yaw_balanced_flag, B_matrix[4×n], rank_B, cond_B |
| **Kabul Kriteri** | KK-13: \|Q_yaw\| ≤ 0.01 N·m \| rank(B) = 4 \| cond(B) < 50 \| Pydantic PASS |
| **Sonraki WBS** | WBS 2.4 OpenVSP 3D \| WBS 7.2 Motor Mixing Matrix \| WBS 7.3 PID Tasarımı |
| **Standartlar** | Prouty §4 \| Mahony 2012 \| PX4 Mixer Docs v1.13 \| ADS-33E-PRF §3.3.5 |

---

## 🔟 4 Adımlı Algoritma

### Adım 1: Q_drag Hesabı

```python
# BEMT varsa bemt.json'dan al; yoksa yaklaşım:
Q_drag = T_per_rotor * D_rotor / (12.0 * FM)   # ±%15 hata marjı

# Kesin yöntem (Prouty §4):
Q_drag = C_Q * rho * n_rps^2 * D^5

# BEMT çıktısından:
Q_drag = P_motor / omega   (omega = 2*pi*RPM/60)
```

**Tipik Q_drag Değerleri:**

| Konfigürasyon | D (m) | MTOW (kg) | T_per_rotor (N) | Q_drag (N·m) |
|---------------|-------|-----------|-----------------|--------------|
| Quad-X küçük | 0.15 | 0.25 | 0.64 | 0.006–0.010 |
| Quad-X orta | 0.24 | 0.90 | 2.30 | 0.020–0.035 |
| Hex-X kargo | 0.38 | 9.0 | 15.5 | 0.12–0.18 |
| Octo-X8 ağır | 0.55 | 25.0 | 32.2 | 0.35–0.55 |
| Dodeca-X12 | 0.65 | 50.0 | 42.6 | 0.55–0.85 |
| Hex-Coax-12 | 0.80 | 80.0 | 67.6 | 1.10–1.60 |

### Adım 2: Yaw Imbalance Kontrolü (KK-13)

```python
sign_i    = +1  if rotation_dirs[i] == 'CW'  else -1
Q_signed  = [sign_i * Q_drag_i  for each rotor i]
Q_yaw     = sum(Q_signed)        # Σ(CW torques) − Σ(CCW torques)

# KK-13 kabul kriteri:
assert abs(Q_yaw) <= 0.01       # N·m
```

**İşaret Kuralı:** CW rotor → +z torque (+1) | CCW rotor → −z torque (−1) | Sağ el kuralı, +z yukarı

> **Coaxial not:** Her kol çiftinde üst-CCW / alt-CW ters dönüş torque'ları büyük ölçüde iptal eder; net Q_kol ≈ 0 ancak küçük FM farkı nedeniyle mükemmel değil — BEMT ile doğrulanmalı.

### Adım 3: Revizyon (KK-13 İhlalinde)

```python
if abs(Q_yaw) > 0.01:
    # Seçenek a: En büyük pozitif Q'yu tersine çevir
    max_idx = argmax(Q_signed)
    rotation_dirs[max_idx] = 'CCW' if 'CW' else 'CW'
    # → config.json güncelle → WBS 2.1'e geri bildir
    
    # Seçenek b: RPM trim (küçük farklar için)
    delta_RPM = Q_imbalance / (dQ_dRPM)   # ±%2 RPM yeterli
    # → WBS 7.2 mixing matrix'e trim ekle
```

### Adım 4: Mixing Matrix B [4×n]

```
B[:,i] = [ k_T,   k_T×y_i,   −k_T×x_i,   sign_i×k_Q ]

Satır 1: Thrust  → tüm motorlar pozitif katkı
Satır 2: Roll    → y_i pozisyona göre (sağ +, sol −)
Satır 3: Pitch   → x_i pozisyona göre (ön −, arka +)
Satır 4: Yaw     → CW=+k_Q, CCW=−k_Q
```

**Konfigürasyona göre rank & cond:**

| Konfigürasyon | n | rank(B) | cond(B) tipik | Durum |
|---------------|---|---------|---------------|-------|
| Quad-X | 4 | 4 | 15–25 | ✅ İyi |
| Hex-X | 6 | 4 | 8–15 | ✅ Çok iyi |
| Y6-Coax | 6 | **3 (risk!)** | — | ⚠️ Dikkat |
| Octo-X8 | 8 | 4 | 5–10 | ✅ Mükemmel |
| X-12 flat | 12 | 4 | 4–8 | ✅ Mükemmel |
| X-16 | 16 | 4 | 3–6 | ✅ Mükemmel |

---

## ✅ Kabul Kriterleri

| Kriter | Parametre | Limit | İhlal Eylemi |
|--------|-----------|-------|--------------|
| **KK-13** | \|Q_yaw_imbalance\| | ≤ 0.01 N·m | rotation_dirs[] revize; RPM trim |
| — | rank(B) | = 4 | Motor konumu veya n_rotors revizyonu |
| — | cond(B) | < 50 | WBS 7.2'de mixing matrix optimizasyonu |
| — | n_CW == n_CCW | True | rotation_dirs[] yeniden ata |

---

## 🔗 WBS Bağlantıları

```
config.json (WBS 2.1)   ──┐
geometry.json (WBS 2.2) ──┤── yaw_balance.py ──► yaw_balance.json
bemt.json (WBS 3.2)     ──┘         │
                                     ├── WBS 2.4 vsp_build.py
          ┌──────────────────────────┤
          │ rotation_dirs revize     └── WBS 7.2 mixing_matrix.py
          ▼                               (B_matrix tam hesap)
   WBS 2.1 config.json            WBS 7.3 pid_design.py
```

---

## yaw_balance.json Şeması (Pydantic YawResult)

```python
class YawResult(BaseModel):
    n_rotors:              int
    rotation_dirs:         List[str]       # güncel (revize edilmiş olabilir)
    Q_per_rotor_Nm:        List[float]     # her motor drag torque
    Q_signed_Nm:           List[float]     # işaretli torque
    Q_yaw_imbalance_Nm:    float           # |val| ≤ 0.01 N·m (KK-13)
    yaw_balanced_flag:     bool            # n_CW == n_CCW
    yaw_OK_flag:           bool            # KK-13 geçildi mi
    rotation_dirs_revised: bool            # revizyon yapıldı mı
    rank_B:                int             # = 4 zorunlu
    cond_B:                float           # < 50 tercih
    validation_passed:     bool = True
```

---

*WBS 2.3 Yaw Torque Dengesi Detay Rehberi v4.0 — Nisan 2026*  
*4 Adım | KK-13 | B-matrix [4×n] | rank & cond kontrolü | Pydantic YawResult*
