"""Multi-objective mode pick.

SNR wants to be high. Latency and power want to be low. A mode is on the
Pareto front when no other mode is better on every objective.
"""

from __future__ import annotations

from dataclasses import dataclass

from network.modehop import MODES, ModeHop


@dataclass
class Objective:
    mode: str
    snr_db: float
    latency_ms: float
    power_w: float

    def dominates(self, other: "Objective") -> bool:
        better_or_equal = self.snr_db >= other.snr_db and self.latency_ms <= other.latency_ms and self.power_w <= other.power_w
        strictly = self.snr_db > other.snr_db or self.latency_ms < other.latency_ms or self.power_w < other.power_w
        return better_or_equal and strictly


def objectives(hop: ModeHop) -> list[Objective]:
    rows = []
    for mode in MODES:
        matched = [row for row in hop.reports if row.mode == mode]
        if not matched:
            continue
        rows.append(Objective(mode, sum(row.snr_db for row in matched) / len(matched), sum(row.latency_ms for row in matched) / len(matched), sum(row.power_w for row in matched) / len(matched)))
    return rows


def pareto(hop: ModeHop) -> list[Objective]:
    found = objectives(hop)
    return [row for row in found if not any(other.dominates(row) for other in found if other.mode != row.mode)]


def pick(hop: ModeHop, prefer: str = "latency_ms") -> dict:
    front = pareto(hop)
    if not front:
        return {"mode": "direct", "front": [], "transmit": False}
    chosen = max(front, key=lambda row: getattr(row, prefer)) if prefer == "snr_db" else min(front, key=lambda row: getattr(row, prefer))
    return {"mode": chosen.mode, "front": [row.mode for row in front], "snr_db": chosen.snr_db, "latency_ms": chosen.latency_ms, "power_w": chosen.power_w, "transmit": False}
