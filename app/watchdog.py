import os
import asyncio
from typing import List, Union
from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from app.config import qctwatchdog_config
from app.messages import DICOMDownloadMessage
from app.qctworksheet import qctworksheet


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
    def construct_dicom_download_message(path) -> Union[DICOMDownloadMessage, None]:
        parent_folder_components = os.path.basename(os.path.dirname(path)).split("_")
        dicom_folder_components = os.path.basename(path).split("_")

        if len(parent_folder_components) == 4 and len(dicom_folder_components) == 2:
            proj = parent_folder_components[2]
            study_id = dicom_folder_components[0]
            ct_date = dicom_folder_components[1]
            return DICOMDownloadMessage(
                proj=proj, study_id=study_id, ct_date=ct_date, dcm_path=path
            )
        else:
            logger.error(f"Invalid folder name syntax - Check path: {path}")

    def on_created(self, event):
        if event.is_directory and DICOMFolderHandler.validate_dicom_folder(
            event.src_path
        ):
            dicom_download_message = (
                DICOMFolderHandler.construct_dicom_download_message(event.src_path)
            )
            logger.info(
                f"New scan download detected: Project={dicom_download_message.proj}, StudyID={dicom_download_message.study_id}, CTDate={dicom_download_message.ct_date}, Path={dicom_download_message.dcm_path}"
            )

            if dicom_download_message:
                qctworksheet.add_new_scan(dicom_download_message)


def initiate_qctwatchdog():
    dicom_download_paths = qctwatchdog_config.dicom_download_paths
    qctwatchdog = QCTWorksheetWatcher(dicom_download_paths, DICOMFolderHandler)
    qctwatchdog.run()
