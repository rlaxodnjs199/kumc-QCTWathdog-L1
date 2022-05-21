import os
from dotenv import load_dotenv

load_dotenv()


class QCTWorksheetConfig:
    google_api_token_path = os.environ.get("GOOGLE_API_TOKEN_PATH")
    qctworksheet_api_key = os.environ.get("QCTWORKSHEET_GOOGLE_API_KEY")
    p_drive_path_prefix = os.environ.get("PDRIVE_PATH_PREFIX")


class QCTWatchdogConfig:
    dicom_download_paths = os.environ.get("DICOM_DOWNLOAD_PATHS_TO_WATCH").split(",")
