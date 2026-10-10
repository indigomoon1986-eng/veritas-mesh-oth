"""SPI register map shared by the Pi and the FPGA tile.

Word format on the wire: address byte, then 32-bit little-endian value.
Transmit bit is stripped unless the board is armed and the caller allows it.
"""

from __future__ import annotations

REG_CONTROL = 0x00
REG_FREQ = 0x04
REG_CHIPS = 0x80

CONTROL_HOP = 0x1
CONTROL_TX = 0x2

MAP = {
    REG_CONTROL: "hop enable in bit 0, transmit enable in bit 1",
    REG_FREQ: "NCO word, freq / clock * 2**32",
    REG_CHIPS: "31-chip spreading code, one bit per chip",
}


def encode(addr: int, value: int) -> list[int]:
    return [addr & 0x7F, value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF]
