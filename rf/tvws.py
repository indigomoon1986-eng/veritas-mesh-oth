"""TV white space hop, driven by Sophia.

Sophia picks the next dwell from a list of channels a white space database
has already cleared for this location. An empty list means no hop and no key.
This is Part 15 Subpart H, not amateur and not Part 90.
"""

from __future__ import annotations

from dataclasses import dataclass, field

TVWS = {14: 473.0, 15: 479.0, 16: 485.0, 17: 491.0, 18: 497.0, 19: 503.0, 20: 509.0, 21: 515.0, 22: 521.0, 23: 527.0, 24: 533.0, 25: 539.0, 26: 545.0, 27: 551.0, 28: 557.0, 29: 563.0, 30: 569.0, 31: 575.0, 32: 581.0, 33: 587.0, 34: 593.0, 35: 599.0, 36: 605.0}


@dataclass
class SophiaTvws:
    available: list[int] = field(default_factory=list)
    index: int = 0

    def load(self, channels: list[int]) -> None:
        self.available = [c for c in channels if c in TVWS]
        self.index = 0

    def next_hop(self) -> dict | None:
        if not self.available:
            return None
        channel = self.available[self.index % len(self.available)]
        self.index += 1
        return {"channel": channel, "mhz": TVWS[channel], "keyed": False, "source": "sophia"}
