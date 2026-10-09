"""Key on receive of a verified mesh packet. Not carrier-operated.

An unverified packet unkeys. A verified hello or message keys the configured
band for one dwell, then the caller must unkey. Arm is still required.
"""

from radio.board import RadioBoard


def on_packet(board: RadioBoard, verified: bool, freq_hz: float) -> dict:
    words = board.key_on_receive(verified, freq_hz)
    return {"verified": verified, "tx": board.tx_enabled, "freq_hz": freq_hz, "words": words}
