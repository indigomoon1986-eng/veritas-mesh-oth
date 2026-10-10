"""Part 15 Subpart H TV white space hop, driven by Sophia.

A hop is legal only on a channel a white space database cleared for this
location, at or under the power that database returned. No list, no hop.
"""

from __future__ import annotations

from dataclasses import dataclass, field

TVWS = {14: 473.0, 15: 479.0, 16: 485.0, 17: 491.0, 18: 497.0, 19: 503.0, 20: 509.0, 21: 515.0, 22: 521.0, 23: 527.0, 24: 533.0, 25: 539.0, 26: 545.0, 27: 551.0, 28: 557.0, 29: 563.0, 30: 569.0, 31: 575.0, 32: 581.0, 33: 587.0, 34: 593.0, 35: 599.0, 36: 605.0}


@dataclass
class Part15Tvws:
    rule: str = "47 CFR 15 Subpart H"
    available: dict[int, float] = field(default_factory=dict)
    index: int = 0

    def load(self, cleared: dict[int, float]) -> None:
        self.available = {ch: min(power, 4.0) for ch, power in cleared.items() if ch in TVWS}
        self.index = 0

    def next_hop(self) -> dict | None:
        if not self.available:
            return None
        channels = list(self.available)
        channel = channels[self.index % len(channels)]
        self.index += 1
        return {"rule": self.rule, "channel": channel, "mhz": TVWS[channel], "power_w": self.available[channel], "keyed": False, "source": "sophia"}
