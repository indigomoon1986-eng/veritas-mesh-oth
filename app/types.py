"""Message and plan types for the OTH path."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "oth.yaml"


def load_config(path: Path | None = None) -> dict[str, Any]:
    with open(path or DEFAULT_CONFIG, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@dataclass
class HopPlan:
    mode: str
    freq_hz: float
    band: str
    azimuth_deg: float
    elevation_deg: float
    range_km: float
    fof2_mhz: float
    reflected: bool
    note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Outbound:
    text: str
    mode: str = "nvis"
    azimuth_deg: float = 0.0
    range_km: float = 300.0
    freq_hz: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Frame:
    node_id: str
    text: str
    plan: HopPlan
    weights_re: list[float] = field(default_factory=list)
    weights_im: list[float] = field(default_factory=list)
    nco_word: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "text": self.text,
            "plan": self.plan.to_dict(),
            "weights_re": self.weights_re,
            "weights_im": self.weights_im,
            "nco_word": self.nco_word,
        }
