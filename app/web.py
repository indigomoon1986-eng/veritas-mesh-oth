"""Web surface on 8788 so it can sit beside the beamform service."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.service import OthApp
from app.types import Outbound, load_config
from mesh.serialize import Concept, Step
from radio.board import RadioBoard
from rf.modulate import modulate
from x402.policy import Amount, requirement, verify

app = FastAPI(title="Veritas Mesh OTH")
oth = OthApp()
board = RadioBoard(load_config())
PRICE = Amount("10000", "USDC")
PAY_TO = "veritas-mesh-treasury"


class SendIn(BaseModel):
    text: str
    mode: str = "nvis"
    azimuth_deg: float = 0.0
    range_km: float = 300.0
    freq_hz: float | None = None


class FeedbackIn(SendIn):
    snr_db: float
    phase_error_deg: float = 0.0


@app.middleware("http")
async def x402_gate(request: Request, call_next):
    if request.url.path != "/send":
        return await call_next(request)
    required = requirement(str(request.url), PRICE, PAY_TO)
    state = verify(required, request.headers.get("PAYMENT-SIGNATURE"))
    if not state.settled:
        return JSONResponse(status_code=402, content={"x402Version": 2, "error": required.error}, headers={"PAYMENT-REQUIRED": required.header()})
    request.state.x402 = state
    return await call_next(request)


@app.get("/health")
def health():
    cfg = load_config()
    return {"node_id": cfg["node_id"], "path": "oth", "ok": True, "armed": board.armed, "tx": board.tx_enabled}


@app.get("/tx")
def tx_page():
    return FileResponse(Path(__file__).with_name("tx.html"))


@app.post("/tx/down")
def tx_down(freq_hz: float):
    board.arm()
    words = board.key(freq_hz)
    return {"armed": True, "tx": board.tx_enabled, "words": words}


@app.post("/tx/up")
def tx_up():
    board.unkey()
    return {"armed": board.armed, "tx": board.tx_enabled}


@app.post("/plan")
def plan(body: SendIn):
    return oth.plan(body.mode, body.azimuth_deg, body.range_km, body.freq_hz).to_dict()


@app.post("/send")
def send(body: SendIn, request: Request):
    out = oth.send(Outbound(body.text, body.mode, body.azimuth_deg, body.range_km, body.freq_hz))
    state = request.state.x402
    concepts = [Concept(1, "x402"), Concept(2, state.required.atomic)]
    steps = [Step(1, 1, 2)]
    out["x402"] = {"paid": state.settled, "amount": state.required.atomic, "payer": state.payer}
    out["modulated"] = modulate(concepts, steps, out["frame"]["plan"]["freq_hz"], b"x402")
    return out


@app.post("/feedback")
def feedback(body: FeedbackIn):
    msg = Outbound(body.text, body.mode, body.azimuth_deg, body.range_km, body.freq_hz)
    return oth.feedback(msg, body.snr_db, body.phase_error_deg)


def main() -> None:
    import uvicorn
    cfg = load_config()
    uvicorn.run(app, host="0.0.0.0", port=int(cfg.get("web_port", 8788)))


if __name__ == "__main__":
    main()
