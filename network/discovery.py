"""Hello packets. Presence, timing, and a hybrid capsule. No public path."""

from __future__ import annotations

import time

from crypto.layer import EncryptionLayer
from mesh.protocol import MeshPacket, dumps


def hello(node_id: str, crypto: EncryptionLayer, freq_hz: float) -> dict:
    body = {
        "node_id": node_id,
        "freq_hz": freq_hz,
        "epoch_us": time.monotonic_ns() // 1000,
        "public": {k: v.hex() for k, v in crypto.identity.public_bytes().items()},
        "sealed": crypto.protect("hello"),
    }
    packet = MeshPacket(node_id, "hello", body)
    return {"packet": packet, "raw": dumps(packet)}
