"""Web surface on 8788 so it can sit beside the beamform service."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from app.service import OthApp
from app.types import Outbound, load_config

app = FastAPI(title="Veritas Mesh OTH")
oth = OthApp()


class SendIn(BaseModel):
    text: str
    mode: str = "nvis"
    azimuth_deg: float = 0.0
    range_km: float = 300.0
    freq_hz: float | None = None


class FeedbackIn(SendIn):
    snr_db: float
    phase_error_deg: float = 0.0


@app.get("/health")
def health():
    cfg = load_config()
    return {"node_id": cfg["node_id"], "path": "oth", "ok": True}


@app.post("/plan")
def plan(body: SendIn):
    return oth.plan(body.mode, body.azimuth_deg, body.range_km, body.freq_hz).to_dict()


@app.post("/send")
def send(body: SendIn):
    return oth.send(Outbound(body.text, body.mode, body.azimuth_deg, body.range_km, body.freq_hz))


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
