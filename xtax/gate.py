"""XTAX license gate.

Sits in front of the stream. A closed gate returns no audio.
This is a policy check, not a transmitter key.
"""

from __future__ import annotations


class LicenseGate:
    def __init__(self, required: bool = True):
        self.required = required

    def allow(self, license_ok: bool) -> bool:
        if not self.required:
            return True
        return bool(license_ok)
