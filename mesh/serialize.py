"""Compact frame for a folded concept map and a short logic tape.

No JSON. Layout: magic VTH1, version, counts, concepts, steps.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

MAGIC = b"VTH1"


@dataclass
class Concept:
    cid: int
    name: str


@dataclass
class Step:
    op: int
    a: int
    b: int


def pack(concepts: list[Concept], steps: list[Step]) -> bytes:
    body = bytearray()
    body += MAGIC
    body += struct.pack("<BBB", 1, len(concepts), len(steps))
    for concept in concepts:
        name = concept.name.encode()[:16].ljust(16, b"\0")
        body += struct.pack("<H", concept.cid) + name
    for step in steps:
        body += struct.pack("<BBH", step.op, step.a, step.b)
    return bytes(body)


def unpack(blob: bytes) -> tuple[list[Concept], list[Step]]:
    if blob[:4] != MAGIC:
        raise ValueError("not a veritas frame")
    version, n_concepts, n_steps = struct.unpack_from("<BBB", blob, 4)
    if version != 1:
        raise ValueError("unknown frame")
    offset = 7
    concepts = []
    for _ in range(n_concepts):
        cid = struct.unpack_from("<H", blob, offset)[0]
        name = blob[offset + 2 : offset + 18].split(b"\0", 1)[0].decode()
        concepts.append(Concept(cid, name))
        offset += 18
    steps = []
    for _ in range(n_steps):
        op, a, b = struct.unpack_from("<BBH", blob, offset)
        steps.append(Step(op, a, b))
        offset += 4
    return concepts, steps
