from functools import lru_cache
from loguru import logger
import gspread

from app.config import qctworksheet_config
from app.messages import DICOMDownloadMessage


class QCTWorksheet:
    try:
        google_service_account = gspread.service_account(
            filename=qctworksheet_config.google_api_token_path
        )
    except:
        google_service_account = None
        logger.exception("Failed to initiate Google service account")
    try:
        session = google_service_account.open_by_key(
            qctworksheet_config.qctworksheet_api_key
        )
    except:
        session = None
        logger.exception("Failed to initiate Google spread sheet session")

    def add_new_scan(self, scan: DICOMDownloadMessage):
        try:
            QCTWorksheet.session.worksheet(scan.proj).append_row(
                values=[
                    scan.proj,
                    "",
                    "",
                    scan.study_id,
                    scan.ct_date,
                    "",
                    scan.dcm_path,
                    scan.dcm_path,
                ]
            )
            logger.info(f"Successfully added new scan to {scan.proj}")
        except:
            logger.exception(f"Sheet {scan.proj} does not exist")


@lru_cache
def get_qctworksheet():
    return QCTWorksheet()


qctworksheet = get_qctworksheet()
