"""Receive path for an X.4.2 frame.

A sealed frame is opened before unpack. The typed amount is settled against
the expected asset. A mismatch is dropped.
"""

from __future__ import annotations

from mesh.protocol import MeshPacket, dumps, loads
from mesh.serialize import pack, unpack
from x402.frame import concepts_for, steps_for
from x402.rail import Amount, Identity, Intent, Rail, Receipt


def send_frame(node_id: str, intent: Intent, receipt: Receipt, layer=None) -> str:
    blob = pack(concepts_for(intent), steps_for(receipt))
    body: dict = {"receiver": intent.receiver}
    if layer is None:
        body["frame"] = blob.hex()
    else:
        body["sealed"] = layer.protect(blob.hex())
    return dumps(MeshPacket(node_id, "x42", body))


def receive_frame(raw: str, expected: Amount, identity: Identity, layer=None) -> dict:
    try:
        packet = loads(raw)
    except (ValueError, UnicodeDecodeError, TypeError):
        return {"ok": False, "stage": "unpack", "note": "bad packet"}
    if not packet.verify() or packet.kind != "x42":
        return {"ok": False, "stage": "unpack", "note": "not an x42 frame"}
    try:
        if "sealed" in packet.body:
            if layer is None:
                return {"ok": False, "stage": "decrypt", "note": "sealed frame and no key"}
            frame_hex = layer.reveal(packet.body["sealed"])
        else:
            frame_hex = packet.body["frame"]
        concepts, _steps = unpack(bytes.fromhex(frame_hex))
    except (ValueError, KeyError):
        return {"ok": False, "stage": "unpack", "note": "frame does not unpack"}
    if len(concepts) < 3:
        return {"ok": False, "stage": "unpack", "note": "typed amount missing"}
    got = Amount(concepts[1].name, concepts[0].name, concepts[2].name)
    settled = Rail(identity).settle(got, expected)
    if not settled.ok:
        return {"ok": False, "stage": "validation", "note": settled.note, "amount": None}
    return {"ok": True, "stage": "accepted", "note": "typed amount matches", "amount": got, "audit": ["unpack", "validation", "accepted"]}


def on_datagram(raw: str, expected: Amount, identity: Identity) -> dict | None:
    if '"x42"' not in raw:
        return None
    return receive_frame(raw, expected, identity)


def key_if_accepted(board, settled: dict | None, freq_hz: float) -> bool:
    if settled is None or not settled.get("ok") or not getattr(board, "armed", False):
        return False
    board.key_on_receive(True, freq_hz)
    return board.tx_enabled
