"""Signed OTH bulletin. Same MAC pattern as the beamform mesh plane."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from dataclasses import asdict, dataclass, field

MESH_KEY = b"veritas-mesh-dev-key"


@dataclass
class MeshPacket:
    node_id: str
    kind: str
    body: dict
    seq: int = field(default_factory=lambda: int(time.time() * 1000) & 0xFFFFFFFF)
    msg_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    ts: float = field(default_factory=time.time)
    mac: str = ""

    def sign(self, key: bytes = MESH_KEY) -> "MeshPacket":
        self.mac = hmac.new(key, self._canon().encode(), hashlib.sha256).hexdigest()
        return self

    def verify(self, key: bytes = MESH_KEY) -> bool:
        expect = hmac.new(key, self._canon().encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expect, self.mac)

    def _canon(self) -> str:
        return json.dumps({"node_id": self.node_id, "kind": self.kind, "seq": self.seq, "body": self.body}, sort_keys=True, separators=(",", ":"))


def dumps(packet: MeshPacket) -> str:
    packet.sign()
    return json.dumps(asdict(packet))


def loads(raw: str) -> MeshPacket:
    return MeshPacket(**json.loads(raw))
