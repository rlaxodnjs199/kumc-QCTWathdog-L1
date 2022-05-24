import os
import asyncio
from typing import List, Union
from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver
import re

from app.config import QCTWatchdogConfig, QCTWorksheetConfig
from app.models import RawScan
from app.qctworksheet import QCTWorksheet, qctworksheet


class QCTWorksheetWatcher:
    def __init__(self, paths_to_watch: List, handler) -> None:
        self.observer = PollingObserver()
        self.handler = handler()
        self.paths_to_watch = paths_to_watch

    async def _run(self):
        logger.add("logs/qctwatchdog.log", level="DEBUG")
        for path in self.paths_to_watch:
            self.observer.schedule(self.handler, path, recursive=True)
            logger.info(f"The watchdog observer starts watching - {path}")
        self.observer.start()

        try:
            while True:
                await asyncio.sleep(1)
        except:
            self.observer.stop()
            logger.info(f"Observer stopped")

        self.observer.join()

    def run(self):
        asyncio.get_event_loop().run_until_complete(self._run())


class DICOMFolderHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.path = ""

    @staticmethod
    def validate_dicom_folder(path) -> bool:
        return len(os.path.basename(path).split("_")) == 2

    @staticmethod
    def construct_raw_scan(path) -> Union[RawScan, None]:
        parent_folder_components = os.path.basename(os.path.dirname(path)).split("_")
        dicom_folder_components = os.path.basename(path).split("_")

        if len(parent_folder_components) == 4 and len(dicom_folder_components) == 2:
            try:
                proj = parent_folder_components[2]
                study_id = dicom_folder_components[0]
                subj = re.sub(r"[^a-zA-Z0-9]", "", study_id)
                ct_date = dicom_folder_components[1]
                fu = QCTWorksheet.calculate_fu(proj, subj)
                dcm_path = os.path.relpath(path, QCTWorksheetConfig.p_drive_path_prefix)
            except:
                logger.error("Invalid folder name")
                return None

            return RawScan(
                proj=proj,
                subj=subj,
                study_id=study_id,
                ct_date=ct_date,
                fu=fu,
                dcm_path=dcm_path,
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
                    f"New scan download detected: Project={raw_scan.proj}, StudyID={raw_scan.study_id}, CTDate={raw_scan.ct_date}, Path={raw_scan.dcm_path}"
                )
                try:
                    qctworksheet.add_new_scan(raw_scan)
                except:
                    logger.error("Add new scan entry to the QCT Worksheet failed")


def initiate_qctwatchdog():
    dicom_download_paths = QCTWatchdogConfig.dicom_download_paths
    qctwatchdog = QCTWorksheetWatcher(dicom_download_paths, DICOMFolderHandler)
    qctwatchdog.run()
