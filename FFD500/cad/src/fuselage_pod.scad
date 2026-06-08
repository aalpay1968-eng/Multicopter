// FireFiterDrone500 - Gövde Podu (Fuselage)
// OpenSCAD Parametrik Model
// Üretici: FFD500_CAD_Architect

$fn = 100;

// --- PARAMETRELER ---
fuselage_length = 4200; // mm
fuselage_width = 1100; // mm
fuselage_height = 600; // mm
tank_volume = 550; // Litre

// --- GÖVDE PODU ---
module fuselage_pod() {
    // Ana gövde (Hafifletilmiş silindir/kapsül)
    hull() {
        translate([0, 0, 0]) sphere(d=fuselage_height);
        translate([fuselage_length, 0, 0]) sphere(d=fuselage_height * 0.8);
    }
    
    // Tank bölmesi (Gövde içinde boşluk olarak düşünülecek)
    // Not: Gerçek üretimde bu kısım içi boş olacak şekilde tasarlanır.
    color("red", 0.5) {
        translate([fuselage_length/3, 0, 0])
            cube([fuselage_length/2, fuselage_width*0.6, fuselage_height*0.6], center=true);
    }
}

// --- MOTOR MOUNTLARI (VTOL) ---
module vtol_motor_mounts() {
    // Kanat uçlarına monte edilecek basit direkler
    for (i = [-1, 1]) {
        translate([i * 4500, 0, 0]) { // Kanat ucu konumu
            cylinder(h=200, d=50, center=true);
        }
    }
}

// --- MONTAJ ---
color("gray") fuselage_pod();
color("black") vtol_motor_mounts();

echo("FFD500 Fuselage Pod Generated");
