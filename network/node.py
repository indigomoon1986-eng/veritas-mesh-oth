"""python -m network.node

Announces on UDP 48750 and prints the shared hop schedule.
Does not key a transmitter.
"""

from __future__ import annotations

import socket
import time

from app.types import load_config
from crypto.layer import EncryptionLayer
from crypto.hopping import schedule
from network.discovery import Directory


def main() -> None:
    cfg = load_config()
    directory = Directory(cfg["node_id"], EncryptionLayer(), cfg["bands"], int(cfg.get("hop", {}).get("dwell_ms", 250)))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((cfg.get("bind", "0.0.0.0"), int(cfg["mesh_port"])))
    sock.settimeout(0.5)
    print(f"discovery on :{cfg['mesh_port']} as {cfg['node_id']}")
    while True:
        raw = directory.announce()
        sock.sendto(raw.encode(), ("255.255.255.255", int(cfg["mesh_port"])))
        hops = schedule({"bands": cfg["bands"], "hop": cfg.get("hop", {})}, directory.crypto.ensure(), slots=4)
        print(f"slot {hops[0]['slot']} freq {hops[0]['freq_hz']} peers {list(directory.peers)}")
        try:
            packet, _addr = sock.recvfrom(4096)
            peer = directory.ingest(packet.decode())
            if peer:
                print(f"heard {peer.node_id} slot {peer.slot} freq {peer.freq_hz}")
        except TimeoutError:
            pass


if __name__ == "__main__":
    main()
