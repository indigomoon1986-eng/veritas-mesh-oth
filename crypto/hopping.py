"""Frequency hop schedule and direct-sequence spreading.

Both ends share the session key, so they compute the same dwell and the same
chip sequence. Channels are the bands already listed in config.
"""

from __future__ import annotations

import hashlib
import math
import time
from typing import Any


def hop_index(key: bytes, slot: int, n_channels: int) -> int:
    digest = hashlib.sha256(key + slot.to_bytes(8, "little")).digest()
    return int.from_bytes(digest[:4], "little") % n_channels


def current_slot(dwell_ms: int, now: float | None = None) -> int:
    now = time.time() if now is None else now
    return int(now * 1000 // max(dwell_ms, 1))


def nco_word(freq_hz: float, clock_hz: float) -> int:
    return int(round(freq_hz / clock_hz * (1 << 32))) & 0xFFFFFFFF


def schedule(cfg: dict[str, Any], key: bytes, now: float | None = None, slots: int = 8) -> list[dict]:
    channels = [float(b["hz"]) for b in cfg["bands"]]
    names = [b["name"] for b in cfg["bands"]]
    dwell = int(cfg.get("hop", {}).get("dwell_ms", 250))
    clock = float(cfg.get("sample_clock_hz", 50_000_000))
    start = current_slot(dwell, now)
    rows = []
    for n in range(slots):
        slot = start + n
        idx = hop_index(key, slot, len(channels))
        freq = channels[idx]
        rows.append({"slot": slot, "channel": idx, "band": names[idx], "freq_hz": freq, "dwell_ms": dwell, "nco_word": nco_word(freq, clock)})
    return rows


def lfsr_code(seed: int, length: int = 31) -> list[int]:
    state = (seed & 0x1F) or 1
    chips = []
    for _ in range(length):
        chips.append(1 if state & 1 else -1)
        bit = (state ^ (state >> 1)) & 1
        state = ((state >> 1) | (bit << 4)) & 0x1F
    return chips


def spreading_code(key: bytes, length: int = 31) -> list[int]:
    seed = int.from_bytes(hashlib.sha256(b"dsss" + key).digest()[:1], "little")
    return lfsr_code(seed, length)


def spread(bits: list[int], chips: list[int]) -> list[int]:
    out = []
    for bit in bits:
        sign = 1 if bit else -1
        out.extend(sign * c for c in chips)
    return out


def despread(samples: list[int], chips: list[int]) -> list[int]:
    n = len(chips)
    bits = []
    for i in range(0, len(samples) - n + 1, n):
        corr = sum(samples[i + k] * chips[k] for k in range(n))
        bits.append(1 if corr > 0 else 0)
    return bits


def processing_gain_db(chips: int) -> float:
    return 10.0 * math.log10(max(chips, 1))
