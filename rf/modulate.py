"""Modulation plan for a serialized frame.

Bytes become 2-FSK symbols on the current skywave hop. Does not key the radio.
"""

from __future__ import annotations

from crypto.hopping import nco_word, spreading_code
from mesh.serialize import pack

SHIFT_HZ = 200.0


def symbols(blob: bytes) -> list[int]:
    out = []
    for byte in blob:
        for bit in range(8):
            out.append((byte >> bit) & 1)
    return out


def modulate(concepts, steps, freq_hz: float, key: bytes, clock_hz: float = 50_000_000) -> dict:
    blob = pack(concepts, steps)
    bits = symbols(blob)
    return {
        "bytes": len(blob),
        "bits": len(bits),
        "mark_hz": freq_hz + SHIFT_HZ,
        "space_hz": freq_hz - SHIFT_HZ,
        "nco_mark": nco_word(freq_hz + SHIFT_HZ, clock_hz),
        "nco_space": nco_word(freq_hz - SHIFT_HZ, clock_hz),
        "symbols": bits,
        "chips": spreading_code(key),
        "transmit": False,
    }
