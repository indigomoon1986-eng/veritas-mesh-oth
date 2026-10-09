"""Encryption layer. Sits between the application and the mesh.

Every bulletin body passes through protect(). The mesh sees ciphertext only.
Session setup is hybrid: X25519 and ML-KEM-768, then ChaCha20-Poly1305.
"""

from __future__ import annotations

from crypto.payload import HybridKey, decapsulate, encapsulate, open_seal, seal

AAD = b"veritas-oth"


class EncryptionLayer:
    def __init__(self) -> None:
        self.identity = HybridKey.generate()
        self.session_key: bytes | None = None
        self.peer: str = ""

    def bind(self, peer_public: dict[str, bytes], peer_id: str = "") -> dict[str, str]:
        capsule, key = encapsulate(peer_public)
        self.session_key = key
        self.peer = peer_id
        return {name: blob.hex() for name, blob in capsule.items()}

    def accept(self, capsule_hex: dict[str, str], peer_id: str = "") -> None:
        capsule = {name: bytes.fromhex(blob) for name, blob in capsule_hex.items()}
        self.session_key = decapsulate(self.identity, capsule)
        self.peer = peer_id

    def ensure(self) -> bytes:
        if self.session_key is None:
            capsule = self.bind(self.identity.public_bytes(), "loopback")
            self.accept(capsule, "loopback")
        assert self.session_key is not None
        return self.session_key

    def protect(self, plaintext: str) -> dict[str, str]:
        key = self.ensure()
        blob = seal(key, plaintext.encode(), AAD)
        return {"nonce": blob["nonce"].hex(), "ct": blob["ct"].hex(), "aad": AAD.decode()}

    def reveal(self, envelope: dict[str, str]) -> str:
        key = self.ensure()
        blob = {"nonce": bytes.fromhex(envelope["nonce"]), "ct": bytes.fromhex(envelope["ct"])}
        return open_seal(key, blob, AAD).decode()
