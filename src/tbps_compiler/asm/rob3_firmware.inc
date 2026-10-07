;==============================================================================
; rob3_firmware.inc — ROB3 8031 firmware equates (IRAM map + routine entries)
;------------------------------------------------------------------------------
; The firmware RAM layout and routine entry points the hosted-mode compiled code
; reuses. The TBPS compiled backend (`tbpsc --arch mcs51`) includes this alongside
; tbps_isa.inc so generated code can mov/orl the firmware state and lcall its
; helpers symbolically instead of with magic literals.
;
; All values are [BYTE]/[SIM]-verified against the ROB3 8031 ROM.
;
; SOURCE OF TRUTH: the ROB3 8031 ROM. This file is a self-contained MIRROR of
; the verified IRAM map + routine entries so the standalone compiler repo needs
; no cross-repo include.
;
;   Syntax: SDAS/ASxxxx (sdas8051).  `.include "rob3_firmware.inc"`.
;==============================================================================

;------------------------------------------------------------------------------
; Firmware IRAM map the hosted-mode compiled code reuses
;------------------------------------------------------------------------------
TARGET_BASE      = 0x40     ; 0x40+N per-axis commanded target (what POS writes)
CURPOS_BASE      = 0x50     ; 0x50+N per-axis current position
FEEDBACK_BASE    = 0x58     ; 0x58+N per-axis ADC feedback
SPEED_BASE       = 0x70     ; 0x70+N per-axis speed/step-rate
NEED_MOVE        = 0x2B     ; axis "needs to move" mask
MOVING           = 0x2C     ; axis "moving" mask
DOUT_SHADOW      = 0x1F     ; digital-out latch shadow (8255 Port B mirror)
PROG_PAGE        = 0x3E     ; ext-RAM program page hi (= 0x80, label table)
PROG_PAGE1       = 0x3F     ; ext-RAM program body page (= 0x81)
PC_LO            = 0x66     ; program counter (ext-RAM offset) lo
PC_HI            = 0x67     ; program counter (ext-RAM offset) hi
STATE_FLAGS      = 0x28     ; .1 loaded, .2 running, .3 motion, .4 conditional

SFR_P1           = 0x90     ; Port 1 (digital inputs read here)

;------------------------------------------------------------------------------
; Firmware routine entry points the compiled code CALLs / mirrors
;------------------------------------------------------------------------------
DOUT_WRITE       = 0x07D0   ; dout_write(A=op[0..3], R0=val) -> DOUT_SHADOW + Port B
PROG_EXEC        = 0x0941   ; stored-program instruction executor
PROG_PREPARE     = 0x0803   ; label-table preprocessor
PROG_GOTO        = 0x0A33   ; label -> PC resolver (rl A x2 into page-0x80 table)

; End of rob3_firmware.inc
