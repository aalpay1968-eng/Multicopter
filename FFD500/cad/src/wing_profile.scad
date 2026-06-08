// FireFiterDrone500 - Ön Kanat Profili (NACA 6412)
// OpenSCAD Parametrik Model
// Üretici: FFD500_CAD_Architect

$fn = 100; // Çözünürlük

// --- PARAMETRELER ---
wing_span = 9000; // mm (Toplam açıklık)
chord_front = 800; // mm (Ön kanat kirişi)
chord_rear = 850; // mm (Arka kanat kirişi)
gap = 1800; // mm (Kanatlar arası mesafe)
thickness_ratio = 0.12; // NACA 6412 kalınlık oranı

// --- NACA 6412 PROFİL FONKSİYONU (Basitleştirilmiş) ---
module naca_profile(chord, thickness) {
    max_thickness = chord * thickness;
    // Gerçek NACA koordinatları buraya dizi olarak eklenebilir
    // Şimdilik basit bir airfoil şekli çiziyoruz
    scale([chord, max_thickness, 1]) {
        circle(d=1); // Temsili profil
    }
}

// --- ÖN KANAT ---
module front_wing() {
    translate([-wing_span/2, 0, 0]) {
        linear_extrude(height = wing_span) {
            // Profil çizimi (2D)
            naca_profile(chord_front, thickness_ratio);
        }
    }
}

// --- ARKA KANAT ---
module rear_wing() {
    translate([-wing_span/2, gap, 0]) {
        linear_extrude(height = wing_span) {
            naca_profile(chord_rear, thickness_ratio);
        }
    }
}

// --- MONTAJ ---
color("blue") front_wing();
color("green") rear_wing();

// Not: Gövde ve motor mountları ayrı modüllerde tanımlanacaktır.
echo("FFD500 Wing Profile Generated");
