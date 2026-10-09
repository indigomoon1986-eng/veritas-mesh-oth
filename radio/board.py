"""Radio board integration.

SPI register map matches veritas-mesh-beamform beamform_top.
0x00 control, 0x04 frequency word, 0x80 chip code.
Transmit enable stays clear. This writes the plan. It does not key the radio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

REG_CONTROL = 0x00
REG_FREQ = 0x04
REG_CHIPS = 0x80
TX_ENABLE = 0x2


def nco_word(freq_hz: float, clock_hz: float = 50_000_000) -> int:
    return int(round(freq_hz / clock_hz * (1 << 32))) & 0xFFFFFFFF


class RadioBoard:
    def __init__(self, cfg: dict[str, Any]):
        self.cfg = cfg
        self.spi_device = cfg.get("radio", {}).get("spi_device", "/dev/spidev0.0")
        self.present = Path(self.spi_device).exists()
        self.last: list[tuple[int, int]] = []
        self.tx_enabled = False

    def probe(self) -> dict[str, Any]:
        return {"spi": self.spi_device, "present": self.present, "tx_enabled": self.tx_enabled, "antenna": "coil-or-vertical", "ground": "copper-rod"}

    def apply_hop(self, freq_hz: float, chips: list[int] | None = None) -> list[tuple[int, int]]:
        word = nco_word(freq_hz, float(self.cfg.get("array", {}).get("sample_clock_hz", 50_000_000)))
        chip_bits = 0
        for i, chip in enumerate((chips or [])[:31]):
            if chip > 0:
                chip_bits |= 1 << i
        words = [(REG_CONTROL, 0x1), (REG_FREQ, word), (REG_CHIPS, chip_bits), (REG_CONTROL, 0x0)]
        self.last = words
        self.tx_enabled = False
        if self.present:
            self._spi_write(words)
        return words

    def _spi_write(self, words: list[tuple[int, int]]) -> None:
        try:
            import spidev
            spi = spidev.SpiDev()
            spi.open(0, 0)
            spi.max_speed_hz = int(self.cfg.get("radio", {}).get("spi_speed_hz", 8_000_000))
            for addr, val in words:
                if addr == REG_CONTROL:
                    val &= ~TX_ENABLE
                spi.xfer2([addr & 0x7F, val & 0xFF, (val >> 8) & 0xFF, (val >> 16) & 0xFF, (val >> 24) & 0xFF])
            spi.close()
        except Exception:
            self.present = False
