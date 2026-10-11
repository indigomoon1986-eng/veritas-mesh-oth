"""Storm and jam simulation.

A storm raises noise. A jammer raises the floor on one channel. The sim
reports whether the link still closes. It does not key a transmitter.
"""

from __future__ import annotations


def simulate(snr_db: float, storm: bool = False, jammed: bool = False, threshold_db: float = 6.0) -> dict:
    noise = 0.0
    if storm:
        noise += 8.0
    if jammed:
        noise += 12.0
    effective = snr_db - noise
    return {"snr_db": snr_db, "storm": storm, "jammed": jammed, "effective_snr_db": effective, "closes": effective >= threshold_db, "keyed": False}
