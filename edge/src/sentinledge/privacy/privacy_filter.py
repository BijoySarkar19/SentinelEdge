import numpy as np
from sentinledge.privacy.face_detector import FaceAnonymizer
from sentinledge.privacy.plate_detector import LicensePlateAnonymizer

class PrivacyPipeline:
    def __init__(
        self,
        mode: str = "metadata_only",
        anonymization_method: str = "gaussian_blur",
    ):
        self.mode = mode
        self.anonymization_method = anonymization_method
        self.face_anonymizer = FaceAnonymizer()
        self.face_anonymizer.load()
        self.plate_anonymizer = LicensePlateAnonymizer()

    def process(self, frame: np.ndarray) -> tuple[np.ndarray | None, dict]:
        """
        Processes frame according to Privacy-First architecture.
        In 'metadata_only' mode: raw frames are NEVER returned or stored.
        """
        stats = {
            "mode": self.mode,
            "faces_anonymized": 0,
            "plates_anonymized": 0,
            "raw_video_retained": False,
        }

        if self.mode == "metadata_only":
            return None, stats

        # Blurred preview mode
        anonymized_frame, faces = self.face_anonymizer.detect_and_anonymize(frame, self.anonymization_method)
        anonymized_frame, plates = self.plate_anonymizer.detect_and_anonymize(anonymized_frame)

        stats["faces_anonymized"] = faces
        stats["plates_anonymized"] = plates
        return anonymized_frame, stats
