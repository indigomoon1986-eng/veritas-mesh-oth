"""python -m network.node

Announces on UDP 48750. An accepted x42 frame can key the radio if armed.
A failed settle does not key. Does not key on an open carrier.
"""

from __future__ import annotations

import socket
import time

from app.types import load_config
from crypto.layer import EncryptionLayer
from crypto.hopping import spreading_code
from network.discovery import Directory
from radio.board import RadioBoard
from x402.rail import Amount, Identity
from x402.receive import key_if_accepted, on_datagram


def main() -> None:
    cfg = load_config()
    directory = Directory(cfg["node_id"], EncryptionLayer(), cfg["bands"], int(cfg.get("hop", {}).get("dwell_ms", 250)))
    board = RadioBoard(cfg)
    if cfg.get("radio", {}).get("armed"):
        board.arm()
    expected = Amount(cfg.get("x42", {}).get("quantity", "10000"), cfg.get("x42", {}).get("asset", "USDC"), cfg.get("x42", {}).get("price", "1"))
    identity = Identity(cfg["node_id"], "mlkem768")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((cfg.get("bind", "0.0.0.0"), int(cfg["mesh_port"])))
    sock.settimeout(0.5)
    print(f"discovery on :{cfg['mesh_port']} as {cfg['node_id']}")
    while True:
        raw = directory.announce()
        sock.sendto(raw.encode(), ("255.255.255.255", int(cfg["mesh_port"])))
        hops = directory.hop_lock(cfg["node_id"], time.time()) if cfg["node_id"] in directory.peers else []
        if not hops:
            from crypto.hopping import schedule
            hops = schedule({"bands": cfg["bands"], "hop": cfg.get("hop", {})}, directory.crypto.ensure(), slots=4)
        board.apply_hop(float(hops[0]["freq_hz"]), spreading_code(directory.crypto.ensure()))
        try:
            packet, _addr = sock.recvfrom(4096)
            text = packet.decode()
            settled = on_datagram(text, expected, identity)
            if settled is not None:
                print(f"x42 {settled['stage']} {settled['note']}")
                if key_if_accepted(board, settled, float(hops[0]["freq_hz"])):
                    print(f"keyed {hops[0]['freq_hz']}")
                if not settled["ok"]:
                    continue
            peer = directory.ingest(text)
            if peer:
                print(f"heard {peer.node_id} slot {peer.slot} freq {peer.freq_hz}")
        except TimeoutError:
            pass


if __name__ == "__main__":
    main()
