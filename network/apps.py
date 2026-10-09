"""Applications on the sealed path: text, a voice frame, a sensor reading."""

from __future__ import annotations

import json

from crypto.layer import EncryptionLayer
from network.routing import HopTable


def frame(kind: str, payload: dict, dest: str, table: HopTable, crypto: EncryptionLayer) -> dict:
    path = table.route(dest)
    sealed = crypto.protect(json.dumps({"kind": kind, "payload": payload}))
    return {
        "kind": kind,
        "dest": dest,
        "path": path,
        "sealed": sealed,
        "e2e": "chacha20-poly1305+x25519+mlkem768",
        "internet": False,
    }


def text(body: str, dest: str, table: HopTable, crypto: EncryptionLayer) -> dict:
    return frame("text", {"text": body}, dest, table, crypto)


def voice(pcm_hex: str, dest: str, table: HopTable, crypto: EncryptionLayer) -> dict:
    return frame("voice", {"pcm": pcm_hex, "rate": 8000}, dest, table, crypto)


def sensor(name: str, value: float, dest: str, table: HopTable, crypto: EncryptionLayer) -> dict:
    return frame("sensor", {"name": name, "value": value}, dest, table, crypto)
