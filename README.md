# Veritas Mesh OTH

Secondary path for over-the-horizon communications on a Veritas node. Local mesh and the beamform plane stay where they are. This path picks a frequency the ionosphere will reflect, steers the array upward, and sends a sealed message frame.

It reuses [veritas-mesh-beamform](https://github.com/indigomoon1986-eng/veritas-mesh-beamform) for the FPGA register map, MIMO weights, and SPI bridge. It does not replace batman-adv or WireGuard.

Licensed amateur (Part 97) or other authorized HF only. The stack plans and frames; it does not key a transmitter by itself.

## Path

app -> crypto (ChaCha20-Poly1305, X25519 + ML-KEM-768) -> mesh (UDP 48750) -> rf -> ionosphere -> fpga / SDR, with feedback returning SNR and phase.

## Run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python3 crypto-init.py
python -m app.cli send --text "node check" --mode nvis
python -m app.cli plan --mode skywave --range-km 800
python -m app.web
pytest -q
```

IP hops leave the Pi through Tor SOCKS on 127.0.0.1:9050. The carrier hops the configured bands on a 250 ms dwell with a 31-chip m-sequence in `fpga/rtl/hop_spread.v`. Part 97 amateur transmissions generally may not hide their meaning. Use the payload cipher on the Tor hop, or on a service that allows cryptography.

# Sovereign Over-the-Horizon Mesh Build Guide

This repo gives you a private, resilient mesh that plans a skywave or near-vertical path when cell towers and the internet go down. The software frames and seals the message. It does not key the radio by itself.

## Hardware You Need

- Raspberry Pi 5 (8 GB recommended)
- SDR or FPGA board, a QuadRF-style 4x4 MIMO tile or similar that can take phase and frequency words
- Resonant coil or vertical antenna tuned to your target band
- Copper ground rod, at least 6-8 feet, driven deep with good soil contact
- Coax or low-loss feed line between the board and antenna
- 5 V 5 A+ power supply for the Pi and board
- Case or enclosure if you want it weatherproof

## Putting It Together

1. Mount the SDR or FPGA board to the Pi using the GPIO header or USB connection.
2. Connect the antenna feed line to the board's RF output.
3. Run a heavy gauge wire from the board's ground plane to the copper rod.
4. Power everything up and confirm the Pi boots and sees the board.

## Software Side

Clone this repo to the Pi:

```bash
git clone https://github.com/indigomoon1986-eng/veritas-mesh-oth.git
cd veritas-mesh-oth
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

Run the init script:

```bash
python3 crypto-init.py
```

Edit `config/oth.yaml` with your node ID and `config/crypto.yaml` with the frequency-hop dwell and key-slot settings.

## First Test, Two Nodes

Set up a second identical Pi and board at least a few miles away, or on the other side of a hill. Both nodes should discover each other through the Veritas mesh, sync timing, and exchange a test message with the payload sealed by ChaCha20-Poly1305 and the hybrid X25519 plus ML-KEM-768 keys.

```bash
python -m app.cli send --text "node check" --mode nvis
```

Once they are framing cleanly, the hop schedule and spread spectrum are already on the carrier: 250 ms dwell, 8 slots, 31-chip m-sequence.

## Next Steps

- Tune the antenna and ground for best coupling.
- Try longer distances or different bands in `config/oth.yaml`.
- Fork the repo and add your own nodes or features.
