"""Beamforming trade: stretch range in rural spots, or cut power on portable gear.

Array gain is 10 log10(N). Rural mode uses the full array. Portable mode
drops elements and scales power. Neither path keys a transmitter.
"""

from __future__ import annotations

import math
from typing import Any


def array_gain_db(n_elements: int) -> float:
    return 10.0 * math.log10(max(n_elements, 1))


def plan(cfg: dict[str, Any], mode: str = "rural", power_w: float = 5.0) -> dict:
    elements = cfg.get("array", {}).get("elements", [])
    n = len(elements) or 1
    if mode == "portable":
        n = max(1, n // 2)
        power_w = power_w * 0.25
    gain = array_gain_db(n)
    range_km = 10.0 * math.sqrt(power_w * (10 ** (gain / 10.0)))
    return {"mode": mode, "elements": n, "gain_db": round(gain, 2), "power_w": round(power_w, 3), "range_km": round(range_km, 1), "keyed": False}
