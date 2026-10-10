"""Payload crypto for the OTH and mesh planes.

ChaCha20-Poly1305 on the message. Session key is a hybrid: X25519 plus ML-KEM-768.
The two shared secrets are concatenated and run through HKDF.

Part 97 forbids obscuring the meaning of an amateur transmission. Part 90
industrial/business may encrypt only on an authorized emission, with a clear ID.
The RF planner still does not key a transmitter.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.mlkem import MLKEM768PrivateKey, MLKEM768PublicKey
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def _hkdf(material: bytes, info: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=b"veritas-oth-v1", info=info).derive(material)


@dataclass
class HybridKey:
    x_private: x25519.X25519PrivateKey
    pq_private: MLKEM768PrivateKey

    @classmethod
    def generate(cls) -> "HybridKey":
        return cls(x25519.X25519PrivateKey.generate(), MLKEM768PrivateKey.generate())

    def public_bytes(self) -> dict[str, bytes]:
        x_pub = self.x_private.public_key().public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        return {"x25519": x_pub, "mlkem768": self.pq_private.public_key().public_bytes_raw()}


def encapsulate(peer_public: dict[str, bytes]) -> tuple[dict[str, bytes], bytes]:
    x_pub = x25519.X25519PublicKey.from_public_bytes(peer_public["x25519"])
    eph = x25519.X25519PrivateKey.generate()
    x_shared = eph.exchange(x_pub)
    x_ct = eph.public_key().public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    pq_pub = MLKEM768PublicKey.from_public_bytes(peer_public["mlkem768"])
    pq_shared, pq_ct = pq_pub.encapsulate()
    key = _hkdf(x_shared + pq_shared, b"session")
    return {"x25519": x_ct, "mlkem768": pq_ct}, key


def decapsulate(local: HybridKey, capsule: dict[str, bytes]) -> bytes:
    peer_eph = x25519.X25519PublicKey.from_public_bytes(capsule["x25519"])
    x_shared = local.x_private.exchange(peer_eph)
    pq_shared = local.pq_private.decapsulate(capsule["mlkem768"])
    return _hkdf(x_shared + pq_shared, b"session")


def seal(key: bytes, plaintext: bytes, aad: bytes = b"") -> dict[str, bytes]:
    nonce = os.urandom(12)
    ct = ChaCha20Poly1305(key).encrypt(nonce, plaintext, aad)
    return {"nonce": nonce, "ct": ct}


def open_seal(key: bytes, blob: dict[str, bytes], aad: bytes = b"") -> bytes:
    return ChaCha20Poly1305(key).decrypt(blob["nonce"], blob["ct"], aad)
