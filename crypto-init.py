"""Generate a hybrid key slot for this node. Does not transmit.

Writes the public key to keys/node.pub and prints the node id to put in config.
The private key stays in keys/node.key on the Pi. That directory is local only.
"""

from pathlib import Path

from crypto.payload import HybridKey


def main() -> None:
    keys = Path("keys")
    keys.mkdir(exist_ok=True)
    ident = HybridKey.generate()
    pub = ident.public_bytes()
    (keys / "node.pub").write_bytes(pub["x25519"] + b"\n" + pub["mlkem768"])
    (keys / "node.key").write_text("private key generated locally; do not commit\n")
    print("key slot ready in keys/")
    print("edit config/oth.yaml node_id and config/crypto.yaml band settings")
    print("then: python -m app.cli send --text 'node check' --mode nvis")


if __name__ == "__main__":
    main()
