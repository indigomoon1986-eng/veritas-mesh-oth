from crypto.hopping import spreading_code
from crypto.payload import HybridKey, decapsulate, encapsulate, open_seal, seal
from app.service import OthApp
from app.types import Outbound


def test_layer_roundtrip():
    from crypto.layer import EncryptionLayer

    alice = EncryptionLayer()
    bob = EncryptionLayer()
    capsule = alice.bind(bob.identity.public_bytes(), "bob")
    bob.accept(capsule, "alice")
    env = alice.protect("node check")
    assert bob.reveal(env) == "node check"
    assert "node check" not in env["ct"]
    alice = HybridKey.generate()
    bob = HybridKey.generate()
    capsule, key_a = encapsulate(bob.public_bytes())
    key_b = decapsulate(bob, capsule)
    assert key_a == key_b
    blob = seal(key_a, b"node check", b"veritas-oth")
    assert open_seal(key_b, blob, b"veritas-oth") == b"node check"


def test_send_hides_plaintext():
    app = OthApp(hour=12)
    out = app.send(Outbound("node check", "nvis"))
    assert out["encrypted"] is True
    assert "node check" not in out["frame"]["text"]
    assert out["frame"]["ip_path"] == "tor-socks"
    assert len(out["frame"]["chips"]) == 31


def test_hop_sequence_agrees():
    from crypto.hopping import despread, schedule, spread

    key = b"shared"
    cfg = {
        "bands": [{"name": "a", "hz": 3590000}, {"name": "b", "hz": 7090000}],
        "hop": {"dwell_ms": 250},
        "sample_clock_hz": 50000000,
    }
    left = schedule(cfg, key, now=1000.0, slots=4)
    right = schedule(cfg, key, now=1000.0, slots=4)
    assert left == right
    chips = spreading_code(key)
    assert despread(spread([1, 0, 1], chips), chips) == [1, 0, 1]
