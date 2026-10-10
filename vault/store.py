"""Recording vault.

Stores stream chunks on disk. The mesh fallback can read the same file
when the regular path is down.
"""

from __future__ import annotations

from pathlib import Path


class Vault:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, name: str) -> Path:
        safe = "".join(c for c in name if c.isalnum() or c in "-_") or "session"
        return self.root / f"{safe}.bin"

    def write(self, name: str, data: bytes) -> Path:
        path = self.path_for(name)
        path.write_bytes(data)
        return path
