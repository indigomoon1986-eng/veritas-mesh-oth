"""Upward steer. Same phase law as the beamform repo."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from app.types import HopPlan

C = 299_792_458.0


def look_vector(azimuth_deg: float, elevation_deg: float) -> np.ndarray:
    az = math.radians(azimuth_deg)
    el = math.radians(elevation_deg)
    return np.array([math.cos(el) * math.sin(az), math.cos(el) * math.cos(az), math.sin(el)])


def weights_for(cfg: dict[str, Any], hop: HopPlan):
    u = look_vector(hop.azimuth_deg, hop.elevation_deg)
    phases = []
    for el in cfg["array"]["elements"]:
        r = np.array([el["x"], el["y"], el["z"]], dtype=float)
        phases.append(-2.0 * math.pi * hop.freq_hz * float(np.dot(r, u)) / C)
    w = np.exp(1j * np.array(phases))
    w = w / (np.linalg.norm(w) + 1e-12)
    clock = float(cfg["array"]["sample_clock_hz"])
    nco = int(round(hop.freq_hz / clock * (1 << 32))) & 0xFFFFFFFF
    return w, nco
