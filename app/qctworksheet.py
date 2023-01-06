from functools import lru_cache
from time import sleep
from loguru import logger
import redis
import gspread
from gspread.exceptions import GSpreadException

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
    try:
        r = redis.Redis(
            host="redis",
            port=6379,
            db=1,
            password=QCTWorksheetConfig.redis_pwd,
        )
    except:
        logger.exception("Failed to connect redis")

    @staticmethod
    def calculate_fu(sheet: str, subj: str) -> int:
        try:
            subj_list = QCTWorksheet.session.worksheet(sheet).findall(subj)
            subj_scan_indexes = {subj.row for subj in subj_list}
        except GSpreadException:
            logger.warning("GSpread Exception: Quota limit")
            sleep(60)
            return QCTWorksheet.calculate_fu(sheet, subj)

        return len(subj_scan_indexes)

    @classmethod
    def check_duplicate(cls, sheet: str, subj: str, ct_date: str):
        if cls.r.get(f"{sheet}_{subj}_{ct_date}"):
            logger.info(f"Redis cache hit - {sheet}_{subj}_{ct_date}")
            return True
        else:
            try:
                subj_scan_list = QCTWorksheet.session.worksheet(sheet).findall(subj)
                for subj_scan in subj_scan_list:
                    subj_scan_ct_date = QCTWorksheet.session.worksheet(
                        sheet
                    ).row_values(subj_scan.row)[4]
                    if subj_scan_ct_date == ct_date:
                        return True
                logger.info(f"Caching the result to Redis - {sheet}_{subj}_{ct_date}")
                cls.r.set(f"{sheet}_{subj}_{ct_date}", "checked")
            except GSpreadException:
                logger.warning("GSpread Exception: Quota limit")
                sleep(60)
                return QCTWorksheet.check_duplicate(sheet, subj, ct_date)

        return False

    @staticmethod
    def add_new_scan(scan: RawScan):
        try:
            QCTWorksheet.session.worksheet(scan.sheet).append_row(
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
            logger.info(f"Successfully added new scan to {scan.sheet}")
        except GSpreadException:
            logger.warning("GSpread Exception: Quota limit")
            sleep(60)
            return QCTWorksheet.add_new_scan(scan)
        except:
            logger.exception(f"Sheet {scan.sheet} does not exist")


@lru_cache
def get_qctworksheet():
    return QCTWorksheet()


qctworksheet = get_qctworksheet()
