from replay.idgen import FakeIdGen, SystemIdGen


def test_fake_idgen_generates_sequential_ids() -> None:
    idgen = FakeIdGen()

    assert idgen.new_id() == "fake-id-1"
    assert idgen.new_id() == "fake-id-2"
    assert idgen.new_id() == "fake-id-3"


def test_system_idgen_generates_unique_ids() -> None:
    idgen = SystemIdGen()

    first_id = idgen.new_id()
    second_id = idgen.new_id()

    assert first_id != second_id