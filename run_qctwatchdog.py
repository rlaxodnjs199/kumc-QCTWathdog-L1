from app.config import QCTWatchdogConfig
from app.qctwatchdog import QCTWatchdog, DICOMFolderHandler


def start_app():
    dicom_paths = QCTWatchdogConfig.dicom_download_paths
    QCTWatchdog(dicom_paths, DICOMFolderHandler).run()


start_app()
