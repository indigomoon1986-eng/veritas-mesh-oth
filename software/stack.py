"""Software module for one sovereign node.

Names the layers and the order a frame moves through them. It does not key
a transmitter.
"""

from __future__ import annotations

from dataclasses import dataclass, field

LAYERS = (
    "application",
    "x42 rail",
    "encryption",
    "mesh",
    "rf control",
    "fpga",
    "hardware abstraction",
)


@dataclass
class SoftwareStack:
    layers: tuple[str, ...] = LAYERS
    transmit: bool = False
    notes: list[str] = field(default_factory=list)

    def path(self) -> list[str]:
        return list(self.layers)

    def describe(self) -> str:
        return " -> ".join(self.layers)
