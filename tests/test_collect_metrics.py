from collector import collect_metrics


def test_collect_metrics_shape():
    m = collect_metrics()
    assert "timestamp" in m
    cpu = m.get("cpu", {})
    assert "total" in cpu
    assert isinstance(cpu.get("per_core"), list)
    assert len(cpu.get("per_core")) >= 1

    memory = m.get("memory", {})
    for k in ["total", "used", "free", "available"]:
        assert k in memory
        assert isinstance(memory[k], int)

    disk = m.get("disk", {})
    assert isinstance(disk, dict)

    network = m.get("network", {})
    assert isinstance(network, dict)
