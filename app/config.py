import os
from dotenv import load_dotenv

load_dotenv()


class QCTWorksheetConfig:
    google_api_token_path = os.path.join(
        os.getcwd(), os.environ.get("GOOGLE_API_TOKEN_PATH")
    )
    qctworksheet_api_key = os.environ.get("QCTWORKSHEET_GOOGLE_API_KEY")
    p_drive_path_prefix = os.environ.get("PDRIVE_PATH_PREFIX")
    proj_to_sheet_mapping = {
        "SARP": "SARP",
        "SARP4": "SARP4",
        "PRECISE": "PRECISE",
        "GALA": "GALA",
        "LHC": "LHC",
        "C19": "C19",
        "CXe": "C19",
        "ILD": "ILD",
        "SSCILD": "ILD",
        "RAILD": "ILD",
        "XeMR": "ILD",
        "ILDKUMR": "ILD",
        "LCP": "LCP",
        "LCPAKB": "LCP",
        "OBERON": "OBERON",
        "Xe-Imaging": "Xe-Imaging",
    }
    redis_pwd = os.environ.get("REDIS_PWD")


class QCTWatchdogConfig:
    dicom_download_paths = os.environ.get("DICOM_DOWNLOAD_PATHS_TO_WATCH").split(",")
