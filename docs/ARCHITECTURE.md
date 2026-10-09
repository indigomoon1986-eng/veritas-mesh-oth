# OTH path

Upward path. Beamform repo remains the local aperture.

1. Application takes a message.
2. Encryption layer seals it.
3. Mesh packet on UDP 48750 carries the frame and the hop plan.
4. RF control asks the ionosphere planner for frequency and elevation.
5. Register writes match beamform_top: 0x04 frequency word, 0x10/0x14 weights.
6. Feedback may lower elevation or hold the carrier. It does not enable transmit.
