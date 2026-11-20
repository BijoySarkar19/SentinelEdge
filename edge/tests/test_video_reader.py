import pytest
from sentinledge.ingestion.video_reader import VideoIngestionSource

def test_video_reader_initialization():
    reader = VideoIngestionSource(uri="test.mp4", frame_skip=3)
    assert reader.uri == "test.mp4"
    assert reader.frame_skip == 3
