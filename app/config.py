import os
from functools import lru_cache
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class QCTWorksheetConfig:
    google_api_token_path = os.environ.get("GOOGLE_API_TOKEN_PATH")
    qctworksheet_api_key = os.environ.get("QCTWORKSHEET_GOOGLE_API_KEY")


@dataclass
class QCTWatchdogConfig:
    dicom_download_paths = os.environ.get("DICOM_DOWNLOAD_PATHS_TO_WATCH").split(",")


qctworksheet_config = QCTWorksheetConfig()
qctwatchdog_config = QCTWatchdogConfig()
