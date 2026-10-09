"""Decentralized mode hop.

Neighbors gossip link quality. Each node votes for ionospheric, ground, or
direct, then follows the local majority. No controller. Does not key the radio.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

MODES = ("ionospheric", "ground", "direct")


@dataclass
class LinkReport:
    peer: str
    mode: str
    snr_db: float
    loss: float


@dataclass
class ModeHop:
    node_id: str
    reports: list[LinkReport] = field(default_factory=list)

    def gossip(self, report: LinkReport) -> None:
        self.reports = [row for row in self.reports if not (row.peer == report.peer and row.mode == report.mode)]
        self.reports.append(report)

    def vote(self) -> str:
        if not self.reports:
            return "direct"
        scores = {mode: 0.0 for mode in MODES}
        for row in self.reports:
            if row.mode not in scores:
                continue
            scores[row.mode] += row.snr_db - 10.0 * row.loss
        best = max(scores, key=scores.get)
        counts = Counter(row.mode for row in self.reports if row.snr_db >= 6)
        if counts and counts.most_common(1)[0][1] >= 2:
            return counts.most_common(1)[0][0]
        return best

    def plan(self) -> dict:
        mode = self.vote()
        if mode == "ionospheric":
            band = {"name": "skywave", "hz_min": 3_000_000, "hz_max": 30_000_000}
        elif mode == "ground":
            band = {"name": "ground", "hz_min": 100_000, "hz_max": 2_000_000}
        else:
            band = {"name": "direct", "hz_min": 144_000_000, "hz_max": 148_000_000}
        return {"node_id": self.node_id, "mode": mode, "band": band, "controller": None, "transmit": False}
