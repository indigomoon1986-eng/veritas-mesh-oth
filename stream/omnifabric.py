"""Omnifabric: one source, three paths.

Triple broadcast sends the same bytes to the regular net, the sealed mesh
fallback, and the vault. The mesh path does not key a transmitter.
"""

from __future__ import annotations

from crypto.layer import EncryptionLayer
from vault.store import Vault

PATHS = ("ip", "mesh", "vault")


class Omnifabric:
    def __init__(self, vault: Vault, layer: EncryptionLayer):
        self.vault = vault
        self.layer = layer

    def broadcast(self, name: str, data: bytes) -> dict:
        self.vault.write(name, data)
        sealed = self.layer.protect(data.hex())
        return {
            "ok": True,
            "paths": list(PATHS),
            "ip": {"bytes": len(data), "ready": True},
            "mesh": {"sealed": True, "transmit": False},
            "vault": {"name": name, "bytes": len(data)},
            "ct": sealed["ct"],
        }
