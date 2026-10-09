# Parallel sovereign network

Every node boots the same image: Pi 5, SDR or FPGA, resonant antenna, copper ground rod, crypto-init.

1. crypto-init loads node id, band, and X25519 plus ML-KEM-768 slots from config.
2. Discovery announces on the Veritas mesh. Hello carries timing and a sealed hybrid capsule.
3. The hop table relays through intermediate nodes. There is no default route to the public internet or a cell tower.
4. Text, voice frames, and sensor readings stay sealed end to end with ChaCha20-Poly1305. Frequency hop and the 31-chip code stay on the carrier.

The stack still does not key a transmitter.
