"""Send path for an X.4.2 intent.

Intent runs the rail. A failed stage never becomes a frame. A good receipt is
packed and handed to the mesh as kind x42. This does not key the radio.
"""

from __future__ import annotations

import socket

from app.types import load_config
from x402.frame import frame_receipt
from x402.rail import Consent, Identity, Intent, Rail
from x402.receive import send_frame


def prepare(identity: Identity, intent: Intent, consent: Consent, freq_hz: float, key: bytes) -> dict:
    receipt = Rail(identity).run(intent, consent)
    if not receipt.ok:
        return {"ok": False, "stage": receipt.stage, "note": receipt.note, "packet": None}
    framed = frame_receipt(intent, receipt, freq_hz, key)
    packet = send_frame(identity.node_id, intent, receipt)
    return {"ok": True, "stage": "sent", "packet": packet, "framed": framed, "transmit": False}


def send(identity: Identity, intent: Intent, consent: Consent, dest: tuple[str, int] | None = None) -> dict:
    cfg = load_config()
    prepared = prepare(identity, intent, consent, float(cfg["bands"][0]["hz"]), b"x42")
    if not prepared["ok"] or dest is None:
        return prepared
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(prepared["packet"].encode(), dest)
    sock.close()
    prepared["sent_to"] = f"{dest[0]}:{dest[1]}"
    return prepared
