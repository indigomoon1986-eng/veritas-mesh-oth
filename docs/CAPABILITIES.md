# Capabilities

Secondary OTH path on the Veritas mesh. Does not key a transmitter.

- Ionosphere planner: NVIS at 80 degrees, skywave elevation from range.
- Encryption layer: ChaCha20-Poly1305, session key from X25519 plus ML-KEM-768.
- Tor SOCKS and hidden service for IP hops before the signal leaves the Pi.
- Frequency hop schedule, 250 ms dwell, 8 slots, shared session key, configured bands only.
- 31-chip m-sequence spread spectrum, FPGA mixer in fpga/rtl/hop_spread.v.
- Feedback holds the carrier when SNR is below the floor.

Part 97 amateur emissions generally may not hide their meaning. Use the cipher on the Tor hop or on a service that allows cryptography.
