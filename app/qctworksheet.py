from functools import lru_cache
from loguru import logger
import gspread

from app.config import QCTWorksheetConfig
from app.models import RawScan


class QCTWorksheet:
    try:
        google_service_account = gspread.service_account(
            filename=QCTWorksheetConfig.google_api_token_path
        )
    except:
        google_service_account = None
        logger.exception("Failed to initiate Google service account")
    try:
        session = google_service_account.open_by_key(
            QCTWorksheetConfig.qctworksheet_api_key
        )
    except:
        session = None
        logger.exception("Failed to initiate Google spread sheet session")

    def calculate_fu(proj: str, subj: str) -> int:
        subj_scan_list = QCTWorksheet.session.worksheet(proj).findall(subj)

        return len(subj_scan_list)

    @staticmethod
    def add_new_scan(scan: RawScan):
        try:
            QCTWorksheet.session.worksheet(scan.proj).append_row(
                values=[
                    scan.proj,
                    scan.subj,
                    "",
                    scan.study_id,
                    scan.ct_date,
                    scan.fu,
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
