import os
import asyncio
from typing import Union
from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver
import re

from app.config import QCTWorksheetConfig
from app.models import RawScan
from app.qctworksheet import QCTWorksheet, qctworksheet


class QCTWatchdog:
    def __init__(self, paths, handler) -> None:
        self.observer = PollingObserver()
        self.handler = handler()
        self.paths = paths

    def _add_paths(self):
        logger.add("logs/qctwatchdog.log", level="DEBUG")
        for path in self.paths:
            self.observer.schedule(self.handler, path, recursive=True)
            logger.info(f"Path Added - {path}")

    async def _run(self):
        self.observer.start()

        try:
            while True:
                await asyncio.sleep(1)
        except:
            self.observer.stop()
            logger.info(f"Observer stopped")

        self.observer.join()

    def run(self):
        self._add_paths()
        asyncio.get_event_loop().run_until_complete(self._run())


class DICOMFolderHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.path = ""

    @staticmethod
    def validate_dicom_folder(path) -> bool:
        return (
            len(os.path.basename(path).split("_")) == 2
            and len(os.path.basename(os.path.dirname(path)).split("_")) == 4
        )

    @staticmethod
    def construct_raw_scan(path) -> Union[RawScan, None]:
        parent_folder_components = os.path.basename(os.path.dirname(path)).split("_")
        dicom_folder_components = os.path.basename(path).split("_")

        if len(parent_folder_components) == 4 and len(dicom_folder_components) == 2:
            try:
                proj = parent_folder_components[2]
                sheet = QCTWorksheetConfig.proj_to_sheet_mapping[proj]
                study_id = dicom_folder_components[0]
                subj = re.sub(r"[^a-zA-Z0-9]", "", study_id)
                ct_date = dicom_folder_components[1]

                if QCTWorksheet.check_duplicate(sheet, subj, ct_date):
                    logger.info(
                        f"Scan already exists in QCTWorksheet: Skip {proj}_{subj}_{ct_date}"
                    )
                    return None

                fu = QCTWorksheet.calculate_fu(sheet, subj)
                dcm_path = os.path.relpath(path, QCTWorksheetConfig.p_drive_path_prefix)
            except:
                logger.error(f"Invalid path - {path}")
                return None

            return RawScan(
                proj=proj,
                subj=subj,
                study_id=study_id,
                ct_date=ct_date,
                fu=fu,
                dcm_path=dcm_path,
                sheet=sheet,
            )
        else:
            logger.error(f"Invalid folder name syntax - Check path: {path}")

    def on_created(self, event):
        if event.is_directory and DICOMFolderHandler.validate_dicom_folder(
            event.src_path
        ):
            raw_scan = DICOMFolderHandler.construct_raw_scan(event.src_path)

            if raw_scan:
                logger.info(
                    f"New scan detected: Project={raw_scan.proj}, StudyID={raw_scan.study_id}, CTDate={raw_scan.ct_date}, Path={raw_scan.dcm_path}"
                )
                try:
                    qctworksheet.add_new_scan(raw_scan)
                except:
                    logger.error("Add new scan entry to the QCT Worksheet failed")
