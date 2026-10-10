"""Named board and live measurements.

The tile is named so gain and power have a place to live. Gain is a register.
Power is read back when the board is present. Neither keys the radio.
"""

from __future__ import annotations

from dataclasses import dataclass

REG_GAIN = 0x08
REG_POWER = 0x0C


@dataclass
class NamedBoard:
    name: str = "veritas-fpga-tile"
    max_gain_db: float = 0.0
    gain_db: float = 0.0
    power_w: float = 0.0

    def set_gain(self, gain_db: float) -> int:
        self.gain_db = max(0.0, min(self.max_gain_db, gain_db))
        return int(round(self.gain_db * 10))

    def read_power(self, raw: int = 0) -> float:
        self.power_w = raw / 1000.0
        return self.power_w
