"""Link to the OTH sibling for longer-range work.

The beamform tree steers. The OTH tree plans the hop. This names the
sibling so a node can hand a long-range plan across.
"""

from __future__ import annotations

SIBLING = "veritas-mesh-oth"


def link(plan: dict) -> dict:
    return {"sibling": SIBLING, "handoff": "oth", "range_km": plan.get("range_km"), "mode": plan.get("mode"), "keyed": False}
