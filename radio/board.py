"""Radio board integration.

apply_hop writes the plan with transmit clear.
key() sets the transmit bit only after an explicit arm, and only on a configured band.
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
        self.armed = False

    def arm(self) -> None:
        self.armed = True

    def key(self, freq_hz: float) -> list[tuple[int, int]]:
        if not self.armed:
            raise RuntimeError("radio is not armed")
        if not self._allowed(freq_hz):
            raise RuntimeError("frequency is not in the configured bands")
        words = self.apply_hop(freq_hz)
        words.append((REG_CONTROL, TX_ENABLE))
        self.last = words
        self.tx_enabled = True
        if self.present:
            self._spi_write([(REG_CONTROL, TX_ENABLE)], allow_tx=True)
        return words

    def unkey(self) -> list[tuple[int, int]]:
        words = [(REG_CONTROL, 0x0)]
        self.last = words
        self.tx_enabled = False
        if self.present:
            self._spi_write(words)
        return words

    def _allowed(self, freq_hz: float) -> bool:
        for band in self.cfg.get("bands", []):
            if abs(float(band["hz"]) - freq_hz) < 1.0:
                return True
        return False

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

    def _spi_write(self, words: list[tuple[int, int]], allow_tx: bool = False) -> None:
        try:
            import spidev
            spi = spidev.SpiDev()
            spi.open(0, 0)
            spi.max_speed_hz = int(self.cfg.get("radio", {}).get("spi_speed_hz", 8_000_000))
            for addr, val in words:
                if addr == REG_CONTROL and not allow_tx:
                    val &= ~TX_ENABLE
                spi.xfer2([addr & 0x7F, val & 0xFF, (val >> 8) & 0xFF, (val >> 16) & 0xFF, (val >> 24) & 0xFF])
            spi.close()
        except Exception:
            self.present = False
