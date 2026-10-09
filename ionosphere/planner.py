"""Ionospheric hop planner.

NVIS is a near-vertical shot, reflected when the carrier is below foF2.
A longer skywave hop uses a lower elevation. Static foF2 curve, not a live ionosonde.
"""

from __future__ import annotations

import math
from typing import Any

from app.types import HopPlan


def fof2_at(cfg: dict[str, Any], hour: int) -> float:
    return float(cfg["ionosphere"]["fof2_mhz"][hour % 24])


def skywave_elevation(range_km: float, height_km: float, floor_deg: float) -> float:
    half = max(range_km, 1.0) / 2.0
    el = math.degrees(math.atan2(height_km, half))
    return max(floor_deg, min(89.0, el))


def pick_band(cfg, mode, fof2_mhz, override_hz):
    if override_hz:
        return "manual", float(override_hz), float(override_hz) / 1e6 < fof2_mhz, "operator frequency"
    bands = cfg["bands"]
    if mode == "nvis":
        usable = [b for b in bands if b.get("nvis") and b["hz"] / 1e6 < fof2_mhz * 0.85]
        if not usable:
            top = bands[0]
            return top["name"], float(top["hz"]), False, "foF2 below configured NVIS bands; plan only, do not transmit"
        best = max(usable, key=lambda b: b["hz"])
        return best["name"], float(best["hz"]), True, "below 0.85 foF2"
    above = [b for b in bands if b["hz"] / 1e6 >= fof2_mhz]
    best = above[0] if above else bands[-1]
    reflected = best["hz"] / 1e6 < fof2_mhz * 3
    note = "one-hop planning band" if reflected else "above typical one-hop MUF for this curve; plan only"
    return best["name"], float(best["hz"]), reflected, note


def plan_hop(cfg, mode, azimuth_deg, range_km, hour, freq_hz=None):
    fo = fof2_at(cfg, hour)
    name, freq, reflected, note = pick_band(cfg, mode, fo, freq_hz)
    if mode == "nvis":
        elev = float(cfg["ionosphere"]["nvis_elevation_deg"])
        range_km = min(range_km, 500.0)
    else:
        elev = skywave_elevation(range_km, float(cfg["ionosphere"]["height_km"]), float(cfg["ionosphere"]["skywave_min_elevation_deg"]))
    return HopPlan(mode, freq, name, azimuth_deg, elev, range_km, fo, reflected, note)
