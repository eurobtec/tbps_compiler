"""Board layer for the compiled backend: ROB3 controller.

TBPS is a **robot-agnostic** language: ``POS 2 . 128`` ("move axis 2 to 128"),
``OUT 1 +`` ("set output 1") and ``TIM 3`` ("wait") are abstract intents. A
:class:`Board` is the upper of the two layers used by the compiled backend (it
sits on an :class:`~tbps_compiler.arch.Arch`) and binds those intents to a
*specific board's* memory map and routines — i.e. how this executor actually
moves an axis or drives a digital output.

The only board shipped today is :data:`ROB3` (hosted/subroutine mode: realize
each intent by reusing the running ROB3 8031 firmware's RAM map + helper
routines, mirroring exactly what the firmware interpreter ``prog_exec`` does per
instruction). Its symbols are defined in rob3_firmware.inc / rob3_sram.inc.
Add another board by constructing another :class:`Board` — no change to the
backend or the arch layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from . import isa
from . import parser as P
from .arch import Arch, MCS51


@dataclass(frozen=True)
class Board:
    """How a specific board/executor realizes each TBPS intent in 8051 asm.

    Only the *board-specific* realizations live here (POS, POS-store, OUT, and
    the TIM counter load). Control flow, the TIM busy-wait skeleton and the
    input-bit addressing are architecture-level (see :class:`Arch`).
    """

    name: str
    arch: Arch
    #: Equate-header ``.include`` names this board needs (RAM map, routines).
    includes: tuple[str, ...]
    emit_pos: Callable[[P.PosAxis, List[str]], None]
    emit_pos_store: Callable[[P.PosStore, List[str]], None]
    emit_out: Callable[[P.Out, List[str]], None]
    #: Load the TIM delay counter bytes (the arch supplies the wait loop).
    emit_tim_load: Callable[[P.Tim, List[str]], None]
    #: One-line description for the generated-file banner.
    banner: str = ""


# =============================================================================
# ROB3 board — hosted/subroutine mode
# =============================================================================
_ROB3_INCLUDES = ("rob3_firmware.inc", "rob3_sram.inc")


def _rob3_emit_pos(node: P.PosAxis, out: List[str]) -> None:
    axis = isa.axis_user_to_fw(node.axis)
    bit = 1 << axis
    if node.speed is None:
        out.append(f"    ; POS {node.axis} . {node.position}  (move axis {axis})")
        out.append(f"    mov  TARGET_BASE+{axis},#0x{node.position & 0xff:02x}")
    else:
        out.append(f"    ; POS {node.axis} . {node.position} , {node.speed}"
                   f"  (move+speed axis {axis})")
        out.append(f"    mov  TARGET_BASE+{axis},#0x{node.position & 0xff:02x}")
        out.append(f"    mov  SPEED_BASE+{axis},#0x{node.speed & 0xff:02x}")
    out.append(f"    orl  NEED_MOVE,#0x{bit:02x}")
    out.append(f"    orl  MOVING,#0x{bit:02x}")


def _rob3_emit_pos_store(node: P.PosStore, out: List[str]) -> None:
    out.append("    ; POS  (store current position, all axes)")
    for a in range(6):
        out.append(f"    mov  TARGET_BASE+{a},FEEDBACK_BASE+{a}")
    out.append("    mov  NEED_MOVE,#0x3f")
    out.append("    mov  MOVING,#0x3f")


def _rob3_emit_out(node: P.Out, out: List[str]) -> None:
    # Mirror the interpreter EXACTLY (prog_exec 0x09D4): dout_write with
    #   A  = opcode & 3   (op selector: 0=MOV/load, 1=ORL, 2=ANL, 3=XRL)
    #   R0 = operand byte (0x00 for '+', 0x01 for '-')
    op = (node.port - 1) & 0x03
    operand = 0x00 if node.set_low else 0x01
    out.append(f"    ; OUT {node.port} {'+' if node.set_low else '-'}"
               f"  (dout_write A=0x{op:02x}, R0=0x{operand:02x})")
    out.append(f"    mov  r0,#0x{operand:02x}")
    out.append(f"    mov  a,#0x{op:02x}")
    out.append("    lcall DOUT_WRITE")


def _rob3_emit_tim_load(node: P.Tim, out: List[str]) -> None:
    # Load the arch's TIM scratch counter. The firmware interpreter uses a
    # 16-bit counter whose high byte is pre-incremented (0x09E1); mirror it so a
    # hosted run matches the interpreter tick-for-tick.
    t = node.delay & 0xFFFF
    out.append(f"    ; TIM {node.delay}  (delay x100ms)")
    out.append(f"    mov  WAIT_CTR_LO,#0x{t & 0xff:02x}")
    out.append(f"    mov  WAIT_CTR_HI,#0x{((t >> 8) + 1) & 0xff:02x}")


ROB3 = Board(
    name="rob3",
    arch=MCS51,
    includes=_ROB3_INCLUDES,
    emit_pos=_rob3_emit_pos,
    emit_pos_store=_rob3_emit_pos_store,
    emit_out=_rob3_emit_out,
    emit_tim_load=_rob3_emit_tim_load,
    banner="hosted mode: reuses the ROB3 firmware RAM map + DOUT_WRITE",
)


#: Boards available by name (for CLI selection).
BOARDS = {ROB3.name: ROB3}
DEFAULT_BOARD = ROB3
