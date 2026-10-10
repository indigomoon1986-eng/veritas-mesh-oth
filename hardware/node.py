"""Hardware module for one sovereign node.

Names the physical pieces and the software stack that runs on them.
It does not key a transmitter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from software.stack import SoftwareStack


@dataclass
class HardwareNode:
    pi: str = "Raspberry Pi 5"
    board: str = "SDR or FPGA tile"
    antenna: str = "resonant coil or vertical"
    ground: str = "copper rod, 6-8 ft"
    feed: str = "coax or low-loss line"
    power: str = "5 V 5 A"
    spi: str = "/dev/spidev0.0"
    present: dict[str, bool] = field(default_factory=dict)
    software: SoftwareStack = field(default_factory=SoftwareStack)

    def probe(self) -> dict[str, bool]:
        self.present = {"spi": Path(self.spi).exists(), "config": True}
        return self.present

    def bill(self) -> list[str]:
        return [self.pi, self.board, self.antenna, self.ground, self.feed, self.power]

    def design(self) -> dict[str, object]:
        return {"hardware": self.bill(), "software": self.software.path(), "transmit": False}
