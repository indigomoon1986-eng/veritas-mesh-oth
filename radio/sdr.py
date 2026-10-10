"""SDR hardware integration points.

The stack speaks a small register map: control, frequency word, chip code.
A real radio attaches as SPI to an FPGA tile, or USB to an SDR dongle.
Neither path keys a transmitter by itself.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SdrLink:
    kind: str
    device: str
    sample_clock_hz: float = 50_000_000

    def nco(self, freq_hz: float) -> int:
        return int(round(freq_hz / self.sample_clock_hz * (1 << 32))) & 0xFFFFFFFF

    def attach(self) -> dict[str, object]:
        return {"kind": self.kind, "device": self.device, "registers": {"control": 0x00, "freq": 0x04, "chips": 0x80}, "transmit": False}


def fpga_tile(device: str = "/dev/spidev0.0") -> SdrLink:
    return SdrLink("spi-fpga", device)


def usb_sdr(device: str = "rtl0") -> SdrLink:
    return SdrLink("usb-sdr", device, sample_clock_hz=2_048_000)
