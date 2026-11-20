import numpy as np
import pytest
from sentinledge.privacy.privacy_filter import PrivacyPipeline

def test_metadata_only_never_returns_raw_frame():
    pipeline = PrivacyPipeline(mode="metadata_only")
    raw_frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
    processed, stats = pipeline.process(raw_frame)
    assert processed is None
    assert stats["raw_video_retained"] is False
    assert stats["mode"] == "metadata_only"
