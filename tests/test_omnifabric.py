from pathlib import Path

from crypto.layer import EncryptionLayer
from stream.omnifabric import PATHS, Omnifabric
from vault.store import Vault


def test_triple_broadcast_hits_all_three_paths(tmp_path: Path):
    fabric = Omnifabric(Vault(tmp_path), EncryptionLayer())
    out = fabric.broadcast("session", b"live-audio")
    assert out["paths"] == list(PATHS)
    assert out["mesh"]["transmit"] is False
    assert out["vault"]["bytes"] == len(b"live-audio")
    assert tmp_path.joinpath("session.bin").read_bytes() == b"live-audio"
