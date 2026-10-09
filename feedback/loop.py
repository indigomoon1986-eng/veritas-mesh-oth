"""Trim elevation from mesh-reported SNR. Does not key the radio."""

from __future__ import annotations

from app.types import HopPlan


def trim(plan: HopPlan, snr_db: float, phase_error_deg: float, floor_db: float, gain: float, max_step: float) -> HopPlan:
    step = max(-max_step, min(max_step, gain * phase_error_deg))
    elev = max(8.0, min(89.0, plan.elevation_deg - step))
    note = plan.note
    reflected = plan.reflected
    if snr_db < floor_db:
        note = plan.note + "; snr below floor, hold carrier"
        reflected = False
    return HopPlan(plan.mode, plan.freq_hz, plan.band, plan.azimuth_deg, elev, plan.range_km, plan.fof2_mhz, reflected, note)
