"""Same image on every node. Hardware is declared, not discovered."""

from __future__ import annotations

from app.types import load_config

IMAGE = {
    "name": "veritas-sovereign-node",
    "board": "raspberry-pi-5",
    "radio": "sdr-or-fpga",
    "antenna": "resonant-coil-or-vertical",
    "ground": "copper-rod-6-8ft",
    "init": "crypto-init.py",
}


def boot(cfg: dict | None = None) -> dict:
    cfg = cfg or load_config()
    return {
        "image": IMAGE,
        "node_id": cfg["node_id"],
        "band": cfg["bands"][0]["name"],
        "key_slots": ["x25519", "mlkem768"],
        "internet": False,
        "cell": False,
    }
