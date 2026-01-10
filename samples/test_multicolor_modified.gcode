; ============================================
; Modified by Splice3D Post-Processor
; 
; This G-code has been modified for use with
; pre-spliced multi-color filament.
; 
; Tool change commands have been removed.
; Load your Splice3D spool before printing.
; ============================================

; Sample multi-color G-code for testing Splice3D
; This simulates a simple two-color print
; Generated manually for testing purposes

; === START G-CODE ===
G28 ; Home all axes
G1 Z5 F3000 ; Lift
M104 S200 ; Set hotend temp
M140 S60 ; Set bed temp
M109 S200 ; Wait for hotend
M190 S60 ; Wait for bed
G92 E0 ; Reset extruder
; === END START G-CODE ===

; Initial purge line
G1 X10 Y10 F3000
G1 Z0.3
; SPLICE3D: Removed T0 ; Tool 0 - White
G1 X100 E10 F1500 ; Purge line - 10mm extruded
G1 E9.8 F3000 ; Retract
G1 Z1

; === LAYER 0 ===
;LAYER:0
G1 X50 Y50 Z0.2 F3000

; First segment - White (T0)
G1 X60 Y50 E10.5 F1200
G1 X60 Y60 E11.0 F1200
G1 X50 Y60 E11.5 F1200
G1 X50 Y50 E12.0 F1200
; Square perimeter done - about 2mm extruded

; Infill
G1 X51 Y51 E12.1 F1200
G1 X59 Y59 E13.0 F1200
G1 X51 Y59 E13.5 F1200
G1 X59 Y51 E14.0 F1200
; More infill
G1 X52 Y52 E14.2 F1200
G1 X58 Y58 E14.8 F1200
; About 4.8mm total for this segment

; === PRIME TOWER ===
G1 X120 Y120 Z0.2 F6000 ; Move to prime tower
G1 X130 Y120 E15.5 F1200
G1 X130 Y130 E16.0 F1200
G1 X120 Y130 E16.5 F1200
G1 X120 Y120 E17.0 F1200
; Prime tower adds about 2mm

; === TOOL CHANGE ===
; SPLICE3D: Removed T1 ; Tool 1 - Black

; Purge at prime tower
G1 X121 Y121 E17.5 F1200
G1 X129 Y121 E18.0 F1200
G1 X129 Y129 E18.5 F1200
G1 X121 Y129 E19.0 F1200
G1 X121 Y121 E19.5 F1200
; Purge adds 2.5mm

; === Continue LAYER 0 with Black ===
G1 X70 Y50 Z0.2 F6000

; Second color region
G1 X80 Y50 E20.5 F1200
G1 X80 Y60 E21.0 F1200
G1 X70 Y60 E21.5 F1200
G1 X70 Y50 E22.0 F1200
; Square done

; Infill for black region
G1 X71 Y51 E22.2 F1200
G1 X79 Y59 E23.0 F1200
G1 X71 Y59 E23.5 F1200
G1 X79 Y51 E24.0 F1200
; About 4mm for black region

; === LAYER 1 ===
;LAYER:1
G1 Z0.4 F3000

; Prime tower layer 1
G1 X120 Y120 F6000
G1 X130 Y120 E24.5 F1200
G1 X130 Y130 E25.0 F1200
G1 X120 Y130 E25.5 F1200
G1 X120 Y120 E26.0 F1200

; Back to model - still black
G1 X70 Y50 F6000
G1 X80 Y50 E27.0 F1200
G1 X80 Y60 E27.5 F1200
G1 X70 Y60 E28.0 F1200
G1 X70 Y50 E28.5 F1200
; Black layer 1 done

; === TOOL CHANGE BACK TO WHITE ===
; SPLICE3D: Removed T0

; Purge
G1 X120 Y120 F6000
G1 X121 Y121 E29.0 F1200
G1 X129 Y121 E29.5 F1200
G1 X129 Y129 E30.0 F1200
G1 X121 Y129 E30.5 F1200
G1 X121 Y121 E31.0 F1200

; White region layer 1
G1 X50 Y50 F6000
G1 X60 Y50 E32.0 F1200
G1 X60 Y60 E32.5 F1200
G1 X50 Y60 E33.0 F1200
G1 X50 Y50 E33.5 F1200
; Back to white

; Final infill
G1 X51 Y51 E33.7 F1200
G1 X59 Y59 E34.5 F1200
G1 X51 Y59 E35.0 F1200
G1 X59 Y51 E35.5 F1200

; === END G-CODE ===
G1 E34.5 F3000 ; Retract
G1 Z10 F3000 ; Lift
G1 X0 Y200 F6000 ; Park
M104 S0 ; Hotend off
M140 S0 ; Bed off
M84 ; Motors off
; === END ===
