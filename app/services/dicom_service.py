import io
from pathlib import Path
import os
from fastapi import UploadFile
from typing import List
import uuid

import pydicom

class DicomService:
    def __init__(self, base_save_path="app/data/patients"):
            self.base_save_path = Path(os.path.abspath(base_save_path)) # Получаем абсолютный путь
            self.base_save_path.mkdir(parents=True, exist_ok=True)

    async def process_and_save_dicom(self, files: List[UploadFile]) -> str:
        if not files:
            raise ValueError("No files provided for upload.")
        try:
            contents = await files[0].read()
            await files[0].seek(0)
            ds = pydicom.dcmread(io.BytesIO(contents))
            patient_id = getattr(ds, 'PatientID', str(uuid.uuid4()))
        except Exception:
            patient_id = str(uuid.uuid4())

        patient_folder = self.base_save_path / patient_id
        patient_folder.mkdir(parents=True, exist_ok=True)

        for file in files:
            file_path = patient_folder / file.filename
            with open(file_path, "wb") as f:
                while content := await file.read(1024):
                    f.write(content)
        return patient_id

    def list_all_dicom_files(self) -> List[str]:
        dicom_files = []
        for patient_folder in self.base_save_path.iterdir():
            if patient_folder.is_dir():
                for file in patient_folder.iterdir():
                    if file.is_file() and file.name.lower().endswith(('.dcm', '.dicom')):
                        dicom_files.append(f"{patient_folder.name}/{file.name}")
        return dicom_files

    def get_dicom_file_path(self, patient_id: str, filename: str) -> Path:
        """Возвращает абсолютный путь к DICOM файлу на основе ID пациента и имени файла."""
        file_path = self.base_save_path / patient_id / filename
        print(file_path)
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"DICOM file not found for patient {patient_id} and filename {filename}")
        return file_path