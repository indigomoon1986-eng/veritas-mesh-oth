# Veritas Mesh OTH

Secondary path for over-the-horizon communications on a Veritas node. Local mesh and the beamform plane stay where they are. This path picks a frequency the ionosphere can reflect, steers the array upward, and frames a signed message.

Reuses veritas-mesh-beamform for the FPGA register map and SPI bridge. Does not replace batman-adv or WireGuard. Does not key a transmitter.

Licensed amateur (Part 97) or other authorized HF only.

## Path

app: message or command
mesh: discovery, route, shared timing on UDP 48750
rf: frequency and phase for an upward beam
ionosphere: NVIS vs one-hop skywave
fpga: same beamform_top carrier, phase, MIMO
feedback: SNR and phase back through the mesh

Full tree is in the archive delivered with the node. Sibling repo: veritas-mesh-beamform.
