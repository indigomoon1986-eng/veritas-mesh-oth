"""Live foF2, with the static curve as the fallback.

Tries a public ionosonde summary. If the fetch fails, the planner uses the
24-hour placeholder already in config. This does not key a transmitter.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any

DEFAULT_URL = "https://lgdc.uml.edu/common/DIDBGetValues"


def live_fof2(cfg: dict[str, Any], hour: int, url: str = DEFAULT_URL) -> tuple[float, str]:
    curve = float(cfg["ionosphere"]["fof2_mhz"][hour % 24])
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        value = float(data.get("fof2_mhz", curve))
        return value, "live"
    except Exception:
        return curve, "fallback"
