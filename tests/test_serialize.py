from mesh.serialize import Concept, Step, pack, unpack
from rf.modulate import modulate


def test_frame_roundtrip_without_json():
    concepts = [Concept(1, "node"), Concept(2, "hop")]
    steps = [Step(1, 1, 2)]
    blob = pack(concepts, steps)
    assert blob[:4] == b"VTH1"
    got_concepts, got_steps = unpack(blob)
    assert got_concepts[1].name == "hop"
    assert got_steps[0].b == 2


def test_modulation_stays_unkeyed():
    plan = modulate([Concept(1, "node")], [Step(1, 1, 0)], 7_090_000, b"shared")
    assert plan["transmit"] is False
    assert plan["mark_hz"] - plan["space_hz"] == 400
    assert plan["bits"] == plan["bytes"] * 8
