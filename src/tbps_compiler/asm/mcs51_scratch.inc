;==============================================================================
; mcs51_scratch.inc — generic 8031/MCS-51 scratch IRAM used by the compiled backend
;------------------------------------------------------------------------------
; Free internal-RAM bytes the compiled 8051 backend uses as working storage for
; operations that need no ROB3 firmware binding. These are NOT firmware state —
; they are ordinary scratch locations; a standalone build could use any free
; IRAM bytes.
;
; The specific addresses below (0x1A/0x1B) are chosen to coincide with the ROB3
; interpreter's own delay counters so a hosted compiled run stays bit-compatible
; with the interpreted run (the compiled==interpreter equivalence test). That is a
; CONVENTION for compatibility, not a dependency on firmware behaviour: the TIM
; busy-wait is a pure MCS-51 `djnz` down-counter.
;
;   Syntax: SDAS/ASxxxx (sdas8051).  `.include "mcs51_scratch.inc"`.
;==============================================================================

;------------------------------------------------------------------------------
; TIM software delay counter (generic djnz down-counter; two scratch bytes)
;------------------------------------------------------------------------------
WAIT_CTR_LO      = 0x1A     ; TIM delay counter lo (scratch)
WAIT_CTR_HI      = 0x1B     ; TIM delay counter hi (scratch)

; End of mcs51_scratch.inc
