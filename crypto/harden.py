"""Hardening for adverse links.

Replay window, fixed-size padding, and a rekey counter. These make the mesh
fail closed under loss, replay, and size-based traffic analysis. They do not
key a transmitter, and they do not remove a required station identification.
"""

from __future__ import annotations

import os

PAD = 256


class ReplayWindow:
    def __init__(self, size: int = 1024):
        self.size = size
        self.seen: dict[str, None] = {}

    def accept(self, token: str) -> bool:
        if not token or token in self.seen:
            return False
        self.seen[token] = None
        if len(self.seen) > self.size:
            self.seen.pop(next(iter(self.seen)))
        return True


def pad(data: bytes, length: int = PAD) -> bytes:
    if len(data) > length - 2:
        raise ValueError("payload exceeds pad")
    body = len(data).to_bytes(2, "little") + data
    return body + os.urandom(length - len(body))


def unpad(blob: bytes) -> bytes:
    n = int.from_bytes(blob[:2], "little")
    if n > len(blob) - 2:
        raise ValueError("bad pad")
    return blob[2 : 2 + n]


class SessionBudget:
    def __init__(self, limit: int = 1000):
        self.limit = limit
        self.used = 0

    def tick(self) -> bool:
        self.used += 1
        return self.used <= self.limit
