"""Architecture layer for the compiled backend: Intel 8031 / MCS-51.

This layer owns everything that is a property of the **CPU architecture**, with
no knowledge of any robot or board:

* the instruction idioms the backend emits (``mov``/``orl``/``ljmp``/``djnz``),
* the standard SFRs (Port 1 input bits),
* the IRAM scratch bytes and the ``djnz`` software down-counter used for TIM,
* the control-flow loop-counter scratch region used by counted ``GOTO``.

A :class:`Arch` is the lower of the two layers used by the compiled backend; a
:class:`~tbps_compiler.board.Board` sits on top of it and binds the abstract
TBPS intents (move axis, digital out) to a specific board's memory map.

The only architecture shipped today is :data:`MCS51` (the Intel 8031 the ROB3
controller uses).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from . import parser as P


@dataclass(frozen=True)
class Arch:
    """CPU-architecture facts + instruction idioms for the compiled backend."""

    name: str
    #: Equate-header ``.include`` names this arch needs (e.g. scratch IRAM).
    includes: tuple[str, ...]

    # --- TIM: a pure software djnz down-counter over two scratch bytes -------
    #: Scratch IRAM byte symbols for the TIM delay counter (defined in the
    #: arch's include header). On the ROB3 build these happen to coincide with
    #: the firmware interpreter's own counter so a hosted run stays
    #: bit-compatible, but that is just the chosen default — nothing here
    #: depends on firmware behaviour.
    tim_counter_lo: str = "WAIT_CTR_LO"
    tim_counter_hi: str = "WAIT_CTR_HI"

    #: Base IRAM address for counted-GOTO loop counters (scratch workspace).
    goto_counter_base: int = 0x78

    #: Port-1 SFR base bit address (P1.0). Standard MCS-51 SFR at 0x90.
    p1_bit_base: int = 0x90

    # --- emit helpers --------------------------------------------------------
    def emit_tim_wait(self, node: P.Tim, out: List[str]) -> None:
        """Emit the TIM delay as a two-byte software ``djnz`` down-counter.

        The counter *values* are loaded by the board (``emit_tim_load``); this
        is the pure-arch busy-wait skeleton that spins until both bytes are 0.
        """
        lbl = f"Ltim_{node.line}"
        out.append(f"{lbl}:")
        out.append(f"    mov  a,{self.tim_counter_lo}")
        out.append(f"    orl  a,{self.tim_counter_hi}")
        out.append(f"    jz   {lbl}_done")
        out.append(f"    djnz {self.tim_counter_lo},{lbl}")
        out.append(f"    djnz {self.tim_counter_hi},{lbl}")
        out.append(f"{lbl}_done:")

    def goto_counter(self, index: int) -> int:
        """IRAM scratch byte for the ``index``-th counted-GOTO loop counter."""
        return self.goto_counter_base + (index & 0x07)

    def p1_bit(self, inp: int) -> int:
        """Bit address of the ``inp``-th (1-based) Port-1 input bit."""
        return self.p1_bit_base + ((inp - 1) & 0x07)


#: Intel 8031 / MCS-51 — the architecture of the ROB3 controller.
MCS51 = Arch(name="mcs51", includes=("mcs51_scratch.inc",))

#: Architectures available by name (for CLI selection).
ARCHS = {MCS51.name: MCS51}
DEFAULT_ARCH = MCS51
