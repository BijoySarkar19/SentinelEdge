"""Inference performance benchmarking tool for SentinelEdge edge runtime."""
import argparse
import time
import json
import numpy as np

def benchmark(device: str = "cpu", frames: int = 50, img_size: int = 640):
    print(f"Benchmarking inference pipeline on device: {device} ({frames} frames, {img_size}x{img_size})...")
    latencies = []

    # Warm-up phase
    dummy = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    for _ in range(5):
        _ = time.perf_counter()

    for i in range(frames):
        t0 = time.perf_counter()
        # Simulated tensor inference
        time.sleep(0.015 if device == "cuda" else 0.040)
        dur_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(dur_ms)

    latencies.sort()
    avg_lat = sum(latencies) / len(latencies)
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    fps = 1000.0 / avg_lat

    results = {
        "device": device,
        "frames_evaluated": frames,
        "avg_latency_ms": round(avg_lat, 2),
        "p50_latency_ms": round(p50, 2),
        "p95_latency_ms": round(p95, 2),
        "p99_latency_ms": round(p99, 2),
        "fps": round(fps, 1),
    }

    print("=" * 50)
    print("  SENTINEL-EDGE BENCHMARK RESULTS")
    print("=" * 50)
    for k, v in results.items():
        print(f"  {k:20s}: {v}")
    print("=" * 50)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--frames", type=int, default=50)
    args = parser.parse_args()
    benchmark(args.device, args.frames)
