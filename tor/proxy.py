"""IP hop leaves the Pi through Tor.

Mesh bulletins that are still IP go out a SOCKS port. RF frames never enter Tor.
"""

from __future__ import annotations

import socket
import struct
from pathlib import Path

TORRC = """# Veritas node. Drop in /etc/tor/torrc.d/veritas.conf
SocksPort 9050
HiddenServiceDir /var/lib/tor/veritas
HiddenServicePort 48750 127.0.0.1:48750
HiddenServicePort 8788 127.0.0.1:8788
"""

def write_torrc(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TORRC, encoding="utf-8")
    return path

def socks5_connect(proxy: tuple[str, int], host: str, port: int, timeout: float = 5.0) -> socket.socket:
    sock = socket.create_connection(proxy, timeout=timeout)
    sock.sendall(b"\x05\x01\x00")
    hello = sock.recv(2)
    if hello != b"\x05\x00":
        sock.close()
        raise OSError("socks5 auth rejected")
    host_b = host.encode()
    req = b"\x05\x01\x00\x03" + bytes([len(host_b)]) + host_b + struct.pack("!H", port)
    sock.sendall(req)
    resp = sock.recv(4)
    if len(resp) < 2 or resp[1] != 0:
        sock.close()
        raise OSError("socks5 connect failed")
    atyp = resp[3]
    if atyp == 1:
        sock.recv(6)
    elif atyp == 3:
        n = sock.recv(1)[0]
        sock.recv(n + 2)
    elif atyp == 4:
        sock.recv(18)
    return sock
