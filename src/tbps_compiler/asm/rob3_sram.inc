;==============================================================================
; rob3_sram.inc — ROB3 external-SRAM program store layout
;------------------------------------------------------------------------------
; The external SRAM (HM6264) layout the firmware uses for the stored TBPS
; program: a page-0x80 label->PC table and the page-0x81+ program body of
; 8-byte instruction slots. Included by the compiled backend alongside
; tbps_isa.inc / rob3_firmware.inc.
;
; All values are [BYTE]/[SIM]-verified against the ROB3 8031 ROM. This file is a
; self-contained MIRROR of the verified SRAM program-store layout.
;
;   Syntax: SDAS/ASxxxx (sdas8051).  `.include "rob3_sram.inc"`.
;==============================================================================

;------------------------------------------------------------------------------
; External-SRAM program store
;------------------------------------------------------------------------------
SRAM_LABEL_BASE  = 0x8000   ; page 0x80: 2-byte-per-label PC table
SRAM_BODY_BASE   = 0x8100   ; page 0x81+: program body (8-byte slots)

; End of rob3_sram.inc
