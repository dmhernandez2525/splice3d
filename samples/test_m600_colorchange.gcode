; Sample G-code using M600 color changes (simpler than multi-extruder)
; This is an alternative to T0/T1 tool changes
; Suitable for printers with manual filament change

; === START G-CODE ===
G28 ; Home all axes
M104 S200 ; Set hotend temp
M140 S60 ; Set bed temp
M109 S200 ; Wait for hotend
M190 S60 ; Wait for bed
G92 E0 ; Reset extruder
; === END START G-CODE ===

; First layer - Color A (White)
;LAYER:0
G1 Z0.2 F3000
G1 X50 Y50 F6000
G1 X100 Y50 E5.0 F1200
G1 X100 Y100 E10.0
G1 X50 Y100 E15.0
G1 X50 Y50 E20.0
; Square complete - 20mm extruded

; Infill
G1 X55 Y55 E20.5
G1 X95 Y95 E25.0
G1 X55 Y95 E27.5
G1 X95 Y55 E30.0

; === COLOR CHANGE ===
M600 ; Pause for filament change (Color B - Black)

; Second section - Color B
G1 X110 Y50 E30.5
G1 X160 Y50 E35.0
G1 X160 Y100 E40.0
G1 X110 Y100 E45.0
G1 X110 Y50 E50.0

; Infill for color B
G1 X115 Y55 E50.5
G1 X155 Y95 E55.0
G1 X115 Y95 E57.5
G1 X155 Y55 E60.0

; === COLOR CHANGE ===
M600 ; Back to Color A

; Third section
;LAYER:1
G1 Z0.4 F3000
G1 X50 Y50 E60.5
G1 X100 Y50 E65.0
G1 X100 Y100 E70.0
G1 X50 Y100 E75.0
G1 X50 Y50 E80.0

; === COLOR CHANGE ===
M600 ; Color B again

G1 X110 Y50 E80.5
G1 X160 Y50 E85.0
G1 X160 Y100 E90.0
G1 X110 Y100 E95.0
G1 X110 Y50 E100.0

; === END G-CODE ===
G1 E99.0 F3000 ; Retract
G1 Z10 F3000 ; Lift
G1 X0 Y200 F6000 ; Park
M104 S0 ; Hotend off
M140 S0 ; Bed off
M84 ; Motors off
; === END ===
