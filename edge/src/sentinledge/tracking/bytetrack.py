import numpy as np
from dataclasses import dataclass
from typing import Sequence
from sentinledge.detection.base import DetectedObject

@dataclass
class TrackedDetection:
    track_id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]
    dwell_time_seconds: float = 0.0
    first_seen_timestamp: float = 0.0

class MultiObjectTracker:
    """ByteTrack wrapper with non-PII, ephemeral session track IDs."""
    def __init__(self, max_lost_frames: int = 30, iou_threshold: float = 0.4):
        self.max_lost_frames = max_lost_frames
        self.iou_threshold = iou_threshold
        self.next_id = 1
        self.active_tracks: dict[int, TrackedDetection] = {}
        self.lost_counters: dict[int, int] = {}

    def _iou(self, boxA, boxB) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        denom = boxAArea + boxBArea - interArea
        return interArea / denom if denom > 0 else 0.0

    def update(self, detections: list[DetectedObject], timestamp: float) -> list[TrackedDetection]:
        updated_tracks = []
        unmatched_detections = list(detections)

        # Match with active tracks by IoU
        for tid, track in list(self.active_tracks.items()):
            best_iou = 0.0
            best_match_idx = -1
            for idx, det in enumerate(unmatched_detections):
                if det.class_id == track.class_id:
                    score = self._iou(track.bbox, det.bbox)
                    if score > best_iou:
                        best_iou = score
                        best_match_idx = idx

            if best_match_idx >= 0 and best_iou >= self.iou_threshold:
                matched_det = unmatched_detections.pop(best_match_idx)
                track.bbox = matched_det.bbox
                track.confidence = matched_det.confidence
                track.dwell_time_seconds = timestamp - track.first_seen_timestamp
                self.lost_counters[tid] = 0
                updated_tracks.append(track)
            else:
                self.lost_counters[tid] += 1
                if self.lost_counters[tid] <= self.max_lost_frames:
                    updated_tracks.append(track)
                else:
                    del self.active_tracks[tid]
                    del self.lost_counters[tid]

        # Register new detections
        for det in unmatched_detections:
            tid = self.next_id
            self.next_id += 1
            t = TrackedDetection(
                track_id=tid,
                class_id=det.class_id,
                class_name=det.class_name,
                confidence=det.confidence,
                bbox=det.bbox,
                dwell_time_seconds=0.0,
                first_seen_timestamp=timestamp,
            )
            self.active_tracks[tid] = t
            self.lost_counters[tid] = 0
            updated_tracks.append(t)

        return updated_tracks
