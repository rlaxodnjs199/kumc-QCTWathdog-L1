from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass
class DICOMDownloadMessage:
    proj: str
    study_id: str
    ct_date: date
    dcm_path: Path
