"""Build an OTH frame and the register writes the beamform FPGA already understands."""

from __future__ import annotations

import json
from datetime import datetime

from app.types import Frame, Outbound, load_config
from crypto.hopping import processing_gain_db, schedule, spread, spreading_code
from crypto.layer import EncryptionLayer
from feedback.loop import trim
from ionosphere.planner import plan_hop
from mesh.protocol import MeshPacket, dumps
from rf.steer import weights_for

REG_FREQ = 0x04
REG_W_RE = 0x10
REG_W_IM = 0x14
SCALE = 32767


class OthApp:
    def __init__(self, hour: int | None = None):
        self.cfg = load_config()
        self.hour = datetime.now().hour if hour is None else hour
        self.crypto = EncryptionLayer()

    def bind_peer(self, peer_public: dict[str, bytes]) -> dict[str, str]:
        return self.crypto.bind(peer_public)

    def accept_capsule(self, capsule: dict[str, str]) -> None:
        self.crypto.accept(capsule)

    def plan(self, mode: str, azimuth_deg: float, range_km: float, freq_hz: float | None = None):
        return plan_hop(self.cfg, mode, azimuth_deg, range_km, self.hour, freq_hz)

    def send(self, msg: Outbound) -> dict:
        hop = self.plan(msg.mode, msg.azimuth_deg, msg.range_km, msg.freq_hz)
        key = self.crypto.ensure()
        hop_cfg = {
            "bands": self.cfg["bands"],
            "hop": self.cfg.get("hop", {"dwell_ms": 250}),
            "sample_clock_hz": self.cfg["array"]["sample_clock_hz"],
        }
        hops = schedule(hop_cfg, key, slots=8)
        carrier = hops[0]
        if msg.freq_hz is None:
            hop.freq_hz = float(carrier["freq_hz"])
            hop.band = str(carrier["band"])
        weights, nco = weights_for(self.cfg, hop)
        sealed = self.crypto.protect(msg.text)
        chips = spreading_code(key)
        bits = [b & 1 for b in bytes.fromhex(sealed["ct"])[:4]]
        frame = Frame(self.cfg["node_id"], sealed["ct"], hop, weights.real.tolist(), weights.imag.tolist(), nco)
        body = frame.to_dict()
        body["sealed"] = sealed
        body["layer"] = "chacha20-poly1305+x25519+mlkem768"
        body["chips"] = chips
        body["spread"] = spread(bits, chips)
        body["processing_gain_db"] = round(processing_gain_db(len(chips)), 2)
        body["hop"] = carrier
        body["hops"] = hops
        body["ip_path"] = "tor-socks"
        packet = MeshPacket(self.cfg["node_id"], "oth", body)
        return {"frame": body, "packet": json.loads(dumps(packet)), "fpga": self._words(frame), "transmit": False, "encrypted": True}

    def feedback(self, msg: Outbound, snr_db: float, phase_error_deg: float) -> dict:
        hop = self.plan(msg.mode, msg.azimuth_deg, msg.range_km, msg.freq_hz)
        fb = self.cfg["feedback"]
        trimmed = trim(hop, snr_db, phase_error_deg, fb["snr_floor_db"], fb["phase_gain"], fb["max_step_deg"])
        weights, nco = weights_for(self.cfg, trimmed)
        sealed = self.crypto.protect(msg.text)
        frame = Frame(self.cfg["node_id"], sealed["ct"], trimmed, weights.real.tolist(), weights.imag.tolist(), nco)
        body = frame.to_dict()
        body["sealed"] = sealed
        body["layer"] = "chacha20-poly1305+x25519+mlkem768"
        return {"frame": body, "fpga": self._words(frame), "transmit": False, "encrypted": True}

    def _words(self, frame: Frame) -> list[list[int]]:
        words = [[REG_FREQ, frame.nco_word]]
        for i, (re, im) in enumerate(zip(frame.weights_re, frame.weights_im)):
            words.append([REG_W_RE + 8 * i, int(max(-1.0, min(1.0, re)) * SCALE) & 0xFFFF])
            words.append([REG_W_IM + 8 * i, int(max(-1.0, min(1.0, im)) * SCALE) & 0xFFFF])
        return words
