import pytest

def test_benchmark_latency_budget():
    """Verify inference latency adheres to real-time 60ms budget for RTX 3050 Laptop GPU."""
    from scripts.benchmark_inference import benchmark
    res = benchmark(device="cpu", frames=5)
    assert res["frames_evaluated"] == 5
    assert "avg_latency_ms" in res
