import pytest
from sentinledge.rules.engine import RulesEngine, RuleDefinition
from sentinledge.tracking.bytetrack import TrackedDetection

def test_crowd_density_rule_trigger():
    engine = RulesEngine([
        RuleDefinition(
            rule_id="R1",
            rule_name="Crowd Alert",
            rule_type="crowd_density",
            camera_id="CAM-1",
            zone_id=None,
            threshold_count=3,
            duration_seconds=0.0,
            severity="high",
            cooldown_seconds=10.0,
        )
    ])

    tracks = [
        TrackedDetection(track_id=1, class_id=0, class_name="person", confidence=0.9, bbox=(10,10,20,20)),
        TrackedDetection(track_id=2, class_id=0, class_name="person", confidence=0.88, bbox=(30,30,40,40)),
        TrackedDetection(track_id=3, class_id=0, class_name="person", confidence=0.92, bbox=(50,50,60,60)),
    ]

    triggers = engine.evaluate(tracks, current_time=100.0)
    assert len(triggers) == 1
    assert triggers[0].rule_id == "R1"
    assert triggers[0].severity == "high"

def test_rule_cooldown_prevents_duplicate():
    engine = RulesEngine([
        RuleDefinition(
            rule_id="R1",
            rule_name="Crowd Alert",
            rule_type="crowd_density",
            camera_id="CAM-1",
            zone_id=None,
            threshold_count=2,
            duration_seconds=0.0,
            severity="high",
            cooldown_seconds=60.0,
        )
    ])

    tracks = [
        TrackedDetection(track_id=1, class_id=0, class_name="person", confidence=0.9, bbox=(10,10,20,20)),
        TrackedDetection(track_id=2, class_id=0, class_name="person", confidence=0.9, bbox=(30,30,40,40)),
    ]

    # First trigger
    res1 = engine.evaluate(tracks, current_time=100.0)
    assert len(res1) == 1

    # Second trigger within cooldown
    res2 = engine.evaluate(tracks, current_time=110.0)
    assert len(res2) == 0
