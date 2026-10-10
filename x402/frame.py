"""Drop an X.4.2 receipt onto the VTH1 frame packer.

Concepts are the typed amount. Steps are the audit stages.
"""

from __future__ import annotations

from mesh.serialize import Concept, Step, pack, unpack
from rf.modulate import modulate
from x402.rail import Intent, Receipt

STAGE = {"intent": 1, "identity": 2, "consent": 3, "validation": 4, "execution": 5, "receipt": 6, "audit": 7}


def concepts_for(intent: Intent) -> list[Concept]:
    amount = intent.amount
    return [Concept(1, amount.asset[:16]), Concept(2, amount.quantity[:16]), Concept(3, amount.price[:16]), Concept(4, intent.receiver[:16])]


def steps_for(receipt: Receipt) -> list[Step]:
    return [Step(STAGE.get(stage, 0), 1, 4) for stage in receipt.audit]


def frame_receipt(intent: Intent, receipt: Receipt, freq_hz: float, key: bytes) -> dict:
    concepts = concepts_for(intent)
    steps = steps_for(receipt)
    blob = pack(concepts, steps)
    back_concepts, back_steps = unpack(blob)
    return {"ok": receipt.ok, "bytes": len(blob), "concepts": [c.name for c in back_concepts], "steps": len(back_steps), "modulated": modulate(concepts, steps, freq_hz, key)}
