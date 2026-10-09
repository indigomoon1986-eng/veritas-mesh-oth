"""Node discovery for the sovereign mesh.

A hello announces presence, a public hybrid key, and the current hop slot.
Hearing a hello learns the peer and binds the session so both ends compute
the same frequency schedule. No scan of other people's channels.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from crypto.hopping import schedule
from crypto.layer import EncryptionLayer
from mesh.protocol import MeshPacket, dumps, loads


@dataclass
class Peer:
    node_id: str
    freq_hz: float
    epoch_us: int
    slot: int
    last_seen: float
    public: dict[str, str] = field(default_factory=dict)


@dataclass
class Directory:
    node_id: str
    crypto: EncryptionLayer
    bands: list[dict]
    dwell_ms: int = 250
    peers: dict[str, Peer] = field(default_factory=dict)

    def announce(self, now: float | None = None) -> str:
        hops = schedule({"bands": self.bands, "hop": {"dwell_ms": self.dwell_ms}}, self.crypto.ensure(), now, slots=1)
        current = hops[0]
        body = {
            "node_id": self.node_id,
            "freq_hz": current["freq_hz"],
            "slot": current["slot"],
            "epoch_us": time.monotonic_ns() // 1000,
            "public": {k: v.hex() for k, v in self.crypto.identity.public_bytes().items()},
            "sealed": self.crypto.protect("hello"),
        }
        return dumps(MeshPacket(self.node_id, "hello", body))

    def ingest(self, raw: str) -> Peer | None:
        try:
            packet = loads(raw)
        except (ValueError, UnicodeDecodeError):
            return None
        if not packet.verify() or packet.kind != "hello":
            return None
        body = packet.body
        if "hello" in body.get("sealed", {}).get("ct", ""):
            return None
        peer = Peer(
            node_id=body["node_id"],
            freq_hz=float(body["freq_hz"]),
            epoch_us=int(body["epoch_us"]),
            slot=int(body["slot"]),
            last_seen=time.time(),
            public=body.get("public", {}),
        )
        self.peers[peer.node_id] = peer
        if peer.public:
            pubs = {k: bytes.fromhex(v) for k, v in peer.public.items()}
            self.crypto.bind(pubs, peer.node_id)
        return peer

    def hop_lock(self, peer_id: str, now: float | None = None) -> list[dict]:
        if peer_id not in self.peers:
            raise KeyError(peer_id)
        return schedule({"bands": self.bands, "hop": {"dwell_ms": self.dwell_ms}}, self.crypto.ensure(), now, slots=8)


def hello(node_id: str, crypto: EncryptionLayer, freq_hz: float) -> dict:
    directory = Directory(node_id, crypto, [{"name": "manual", "hz": freq_hz}])
    raw = directory.announce()
    return {"packet": loads(raw), "raw": raw}
