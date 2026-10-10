"""Receive path for an X.4.2 frame.

The sender puts the VTH1 blob in a mesh packet of kind x42. The peer unpacks
before any hop or key, rebuilds the typed amount, and settles it against the
expected asset. A mismatch is dropped.
"""

from __future__ import annotations

from mesh.protocol import MeshPacket, dumps, loads
from mesh.serialize import pack, unpack
from x402.frame import concepts_for, steps_for
from x402.rail import Amount, Identity, Intent, Rail, Receipt


def send_frame(node_id: str, intent: Intent, receipt: Receipt) -> str:
    blob = pack(concepts_for(intent), steps_for(receipt))
    packet = MeshPacket(node_id, "x42", {"frame": blob.hex(), "receiver": intent.receiver})
    return dumps(packet)


def receive_frame(raw: str, expected: Amount, identity: Identity) -> dict:
    try:
        packet = loads(raw)
    except (ValueError, UnicodeDecodeError, TypeError):
        return {"ok": False, "stage": "unpack", "note": "bad packet"}
    if not packet.verify() or packet.kind != "x42":
        return {"ok": False, "stage": "unpack", "note": "not an x42 frame"}
    try:
        concepts, _steps = unpack(bytes.fromhex(packet.body["frame"]))
    except (ValueError, KeyError):
        return {"ok": False, "stage": "unpack", "note": "frame does not unpack"}
    if len(concepts) < 3:
        return {"ok": False, "stage": "unpack", "note": "typed amount missing"}
    got = Amount(concepts[1].name, concepts[0].name, concepts[2].name)
    rail = Rail(identity)
    settled = rail.settle(got, expected)
    if not settled.ok:
        return {"ok": False, "stage": "validation", "note": settled.note, "amount": None}
    return {"ok": True, "stage": "accepted", "note": "typed amount matches", "amount": got, "audit": ["unpack", "validation", "accepted"]}
