from app.service import OthApp
from app.types import Outbound


def test_nvis_points_up():
    app = OthApp(hour=12)
    out = app.send(Outbound("node check", "nvis", 0.0, 200.0))
    assert out["frame"]["plan"]["elevation_deg"] >= 70
    assert out["transmit"] is False
    assert out["packet"]["kind"] == "oth"


def test_skywave_elevation_drops_with_range():
    app = OthApp(hour=14)
    near = app.plan("skywave", 20.0, 400.0)
    far = app.plan("skywave", 20.0, 1600.0)
    assert far.elevation_deg < near.elevation_deg
    assert far.elevation_deg >= 8


def test_weights_match_channel_count():
    app = OthApp(hour=3)
    out = app.send(Outbound("night", "nvis"))
    assert len(out["frame"]["weights_re"]) == 4
    assert out["fpga"][0][0] == 0x04


def test_low_snr_holds():
    app = OthApp(hour=12)
    out = app.feedback(Outbound("node check", "nvis"), snr_db=1.0, phase_error_deg=4.0)
    assert out["frame"]["plan"]["reflected"] is False
    assert "hold carrier" in out["frame"]["plan"]["note"]
