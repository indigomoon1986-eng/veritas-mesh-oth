"""Key the radio. Off until arm() is called. Configured bands only.

Part 97 amateur transmissions must identify and stay inside the privileges of the license.
This sets the FPGA transmit-enable bit. It does not raise power or leave the band list.
"""

from radio.board import RadioBoard


def key_for(board: RadioBoard, freq_hz: float, callsign: str) -> dict:
    if not callsign:
        raise RuntimeError("callsign required before key")
    words = board.key(freq_hz)
    return {"callsign": callsign, "freq_hz": freq_hz, "tx": board.tx_enabled, "words": words}
