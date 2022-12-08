import sys
from multiprocessing import Process

from app.config import QCTWatchdogConfig
from app.watchdog import initiate_qctwatchdog


def start_app():
    dicom_download_paths = QCTWatchdogConfig.dicom_download_paths
    for path in dicom_download_paths:
        process = Process(target=initiate_qctwatchdog, args=(path,))
        process.start()


def add_new_path(path: str):
    initiate_qctwatchdog(path)


if len(sys.argv) == 2:
    dicom_path = sys.argv[1]
    add_new_path(dicom_path)
else:
    start_app()
