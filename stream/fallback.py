"""Mesh fallback for the stream.

When the regular net drops, the same vault file can be sealed and handed
to the mesh as a bulletin. This does not key the radio.
"""

from __future__ import annotations

from crypto.layer import EncryptionLayer
from vault.store import Vault


def fallback(vault: Vault, name: str, layer: EncryptionLayer) -> dict:
    path = vault.path_for(name)
    if not path.exists():
        return {"ok": False, "note": "nothing to fall back"}
    sealed = layer.protect(path.read_bytes().hex())
    return {"ok": True, "sealed": sealed, "transmit": False, "bytes": path.stat().st_size}
