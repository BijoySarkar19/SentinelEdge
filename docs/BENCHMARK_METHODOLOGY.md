# SentinelEdge Inference Benchmark Methodology

## Overview
The benchmark utility measures computer-vision inference latency under controlled conditions without fabricating results.

## Execution Command
```bash
python scripts/benchmark_inference.py --device cpu --frames 100
python scripts/benchmark_inference.py --device cuda --frames 100
```

## Metrics Collected
- **Average Latency**: Mean millisecond execution time per frame.
- **p50 / p95 / p99**: Percentile latency distributions indicating frame consistency.
- **Frames Per Second (FPS)**: Real-time throughput capability.
