"""Core stream server.

Pulls from a file source, or a mic device name when one is present.
Pushes live chunks over WebSocket and HTTP. Does not key a transmitter.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse, StreamingResponse

from vault.store import Vault
from xtax.gate import LicenseGate

app = FastAPI(title="Veritas Stream")
vault = Vault(Path("/tmp/veritas-vault"))
gate = LicenseGate()


def source_chunks(path: Path, size: int = 4096):
    data = path.read_bytes()
    for i in range(0, len(data), size):
        yield data[i : i + size]


@app.get("/player")
def player() -> FileResponse:
    return FileResponse(Path(__file__).with_name("player.html"))


@app.get("/stream/{name}")
def stream(name: str, license_ok: bool = False):
    if not gate.allow(license_ok):
        return {"ok": False, "note": "xtax license gate closed"}
    path = vault.path_for(name)
    if not path.exists():
        return {"ok": False, "note": "no recording"}
    return StreamingResponse(source_chunks(path), media_type="application/octet-stream")


@app.websocket("/live/{name}")
async def live(socket: WebSocket, name: str):
    await socket.accept()
    path = vault.path_for(name)
    if path.exists():
        for chunk in source_chunks(path):
            await socket.send_bytes(chunk)
    await socket.close()
