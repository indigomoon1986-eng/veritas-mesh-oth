"""One path for the stream.

Mic or file goes into the vault. XTAX gates the HTTP and WebSocket out.
If the regular net drops, the same vault file is sealed for the mesh.
Nothing here keys a transmitter.
"""

from __future__ import annotations

from crypto.layer import EncryptionLayer
from stream.fallback import fallback
from vault.store import Vault
from xtax.gate import LicenseGate


class StreamPath:
    def __init__(self, vault: Vault, gate: LicenseGate, layer: EncryptionLayer):
        self.vault = vault
        self.gate = gate
        self.layer = layer

    def ingest(self, name: str, data: bytes) -> str:
        return str(self.vault.write(name, data))

    def serve(self, name: str, license_ok: bool) -> dict:
        if not self.gate.allow(license_ok):
            return {"ok": False, "path": "xtax", "note": "gate closed"}
        path = self.vault.path_for(name)
        if not path.exists():
            return {"ok": False, "path": "vault", "note": "no recording"}
        return {"ok": True, "path": "http", "bytes": path.stat().st_size}

    def mesh_fallback(self, name: str) -> dict:
        return fallback(self.vault, name, self.layer)
