from crypto.layer import EncryptionLayer
from x402.rail import Amount, Consent, Identity, Intent, Rail
from x402.receive import receive_frame, send_frame


def test_sealed_frame_opens_and_settles():
    layer = EncryptionLayer()
    layer.ensure()
    rail = Rail(Identity("veritas-pi-01", "mlkem768"))
    intent = Intent("veritas-pi-01", "veritas-pi-02", Amount("10000", "USDC", "1"), "pay")
    receipt = rail.run(intent, Consent(True, "veritas-pi-01"))
    raw = send_frame("veritas-pi-01", intent, receipt, layer)
    assert "sealed" in raw
    got = receive_frame(raw, Amount("10000", "USDC", "1"), Identity("veritas-pi-02", "mlkem768"), layer)
    assert got["ok"] is True
    assert got["amount"].asset == "USDC"
