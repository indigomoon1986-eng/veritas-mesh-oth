# Veritas Mesh OTH

Secondary path for over-the-horizon communications on a Veritas node. Local mesh and the beamform plane stay where they are. This path picks a frequency the ionosphere will reflect, steers the array upward, and sends a sealed message frame.

It reuses veritas-mesh-beamform for the FPGA register map, MIMO weights, and SPI bridge. It does not replace batman-adv or WireGuard.

Licensed amateur (Part 97) or other authorized HF only. The stack plans and frames; it does not key a transmitter by itself.

## Path

app -> crypto (ChaCha20-Poly1305, X25519 + ML-KEM-768) -> mesh (UDP 48750) -> rf -> ionosphere -> fpga / SDR, with feedback returning SNR and phase.

## Run

python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m app.cli send --text "node check" --mode nvis
python -m app.cli plan --mode skywave --range-km 800
python -m app.web
pytest -q

Sibling repo: https://github.com/indigomoon1986-eng/veritas-mesh-beamform

IP hops leave the Pi through Tor SOCKS on 127.0.0.1:9050. The payload is ChaCha20-Poly1305. The carrier hops the configured bands on a 250 ms dwell with a 31-chip m-sequence in fpga/rtl/hop_spread.v. Part 97 amateur transmissions generally may not hide their meaning.
