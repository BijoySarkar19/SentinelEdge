import time

class PerformanceMonitor:
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.frame_times: list[float] = []
        self.inference_latencies: list[float] = []
        self.total_frames = 0

    def record_frame(self, inference_ms: float):
        now = time.time()
        self.frame_times.append(now)
        self.inference_latencies.append(inference_ms)
        self.total_frames += 1

        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
            self.inference_latencies.pop(0)

    @property
    def fps(self) -> float:
        if len(self.frame_times) < 2:
            return 0.0
        elapsed = self.frame_times[-1] - self.frame_times[0]
        return round(len(self.frame_times) / elapsed, 1) if elapsed > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        if not self.inference_latencies:
            return 0.0
        return round(sum(self.inference_latencies) / len(self.inference_latencies), 1)
