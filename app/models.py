from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass
class RawScan:
    proj: str
    subj: str
    study_id: str
    ct_date: date
    fu: int
    dcm_path: Path
    sheet: str
