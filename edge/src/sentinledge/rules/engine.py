import time
from dataclasses import dataclass, field
from typing import Any, Optional
from sentinledge.tracking.bytetrack import TrackedDetection

@dataclass
class RuleDefinition:
    rule_id: str
    rule_name: str
    rule_type: str  # crowd_density, restricted_zone, vehicle_congestion, access_lane, custom
    camera_id: str
    zone_id: Optional[str]
    threshold_count: int
    duration_seconds: float
    severity: str
    cooldown_seconds: float = 60.0
    enabled: bool = True
    polygon_coordinates: list[list[float]] = field(default_factory=list)

@dataclass
class RuleTriggerResult:
    rule_id: str
    rule_name: str
    event_type: str
    severity: str
    confidence: float
    summary: str
    object_counts: dict[str, int]
    detected_classes: list[str]

class RulesEngine:
    def __init__(self, rules: list[RuleDefinition] | None = None):
        self.rules = rules or []
        self.last_triggered_timestamps: dict[str, float] = {}

    def add_rule(self, rule: RuleDefinition):
        self.rules.append(rule)

    def _point_in_polygon(self, x: float, y: float, poly: list[list[float]]) -> bool:
        if not poly or len(poly) < 3:
            return True
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def evaluate(self, tracks: list[TrackedDetection], current_time: float) -> list[RuleTriggerResult]:
        triggers = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            last_trig = self.last_triggered_timestamps.get(rule.rule_id, 0.0)
            if current_time - last_trig < rule.cooldown_seconds:
                continue

            # Class count aggregation
            counts: dict[str, int] = {}
            matching_tracks = []

            for track in tracks:
                cx = (track.bbox[0] + track.bbox[2]) / 2.0
                cy = (track.bbox[1] + track.bbox[3]) / 2.0
                if self._point_in_polygon(cx, cy, rule.polygon_coordinates):
                    counts[track.class_name] = counts.get(track.class_name, 0) + 1
                    matching_tracks.append(track)

            # Rule A: Crowd density
            if rule.rule_type == "crowd_density":
                person_count = counts.get("person", 0)
                if person_count >= rule.threshold_count:
                    triggers.append(
                        RuleTriggerResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.rule_name,
                            event_type="crowd_density",
                            severity=rule.severity,
                            confidence=0.91,
                            summary=f"Unusual crowd density warning: {person_count} persons detected (threshold: {rule.threshold_count})",
                            object_counts=counts,
                            detected_classes=list(counts.keys()),
                        )
                    )
                    self.last_triggered_timestamps[rule.rule_id] = current_time

            # Rule B: Restricted zone occupancy
            elif rule.rule_type == "restricted_zone":
                violators = [t for t in matching_tracks if t.dwell_time_seconds >= rule.duration_seconds]
                if len(violators) >= rule.threshold_count:
                    triggers.append(
                        RuleTriggerResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.rule_name,
                            event_type="restricted_zone",
                            severity=rule.severity,
                            confidence=0.94,
                            summary=f"Restricted zone occupancy detected: {len(violators)} objects dwelling over {rule.duration_seconds}s",
                            object_counts=counts,
                            detected_classes=list(counts.keys()),
                        )
                    )
                    self.last_triggered_timestamps[rule.rule_id] = current_time

            # Rule C: Vehicle congestion
            elif rule.rule_type == "vehicle_congestion":
                vehicles = sum(counts.get(k, 0) for k in ["car", "bus", "truck", "motorcycle"])
                if vehicles >= rule.threshold_count:
                    triggers.append(
                        RuleTriggerResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.rule_name,
                            event_type="vehicle_congestion",
                            severity=rule.severity,
                            confidence=0.88,
                            summary=f"Vehicle congestion detected: {vehicles} vehicles in monitored segment (threshold: {rule.threshold_count})",
                            object_counts=counts,
                            detected_classes=list(counts.keys()),
                        )
                    )
                    self.last_triggered_timestamps[rule.rule_id] = current_time

            # Rule D: Access lane blockage
            elif rule.rule_type == "access_lane":
                blockers = [t for t in matching_tracks if t.class_name in ["car", "truck", "bus"] and t.dwell_time_seconds >= rule.duration_seconds]
                if len(blockers) >= rule.threshold_count:
                    triggers.append(
                        RuleTriggerResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.rule_name,
                            event_type="access_lane",
                            severity=rule.severity,
                            confidence=0.92,
                            summary=f"Emergency access lane blocked: {len(blockers)} stationary vehicles for over {rule.duration_seconds}s",
                            object_counts=counts,
                            detected_classes=list(counts.keys()),
                        )
                    )
                    self.last_triggered_timestamps[rule.rule_id] = current_time

        return triggers
