from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import pydicom
from typing import List
from app.services.dicom_service import DicomService

router = APIRouter(prefix="/dicom", tags=["DICOM"])
dicom_service = DicomService()

@router.post("/upload/")
async def upload_dicom_file(files: List[UploadFile] = File(...)):
    """Загрузка одного или нескольких DICOM файлов на сервер."""
    try:
        patient_id = await dicom_service.process_and_save_dicom(files)
        return {"message": f"Файлы успешно загружены и сохранены для пациента: {patient_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/")
async def list_dicom_files():
    """Список доступных DICOM файлов."""
    try:
        dicom_files = dicom_service.list_all_dicom_files()
        return JSONResponse({"files": dicom_files})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{patient_id}/{filename}/metadata")
async def get_dicom_metadata(patient_id: str, filename: str):
    """Получение метаданных DICOM файла для конкретного пациента."""
    try:
        file_path = dicom_service.get_dicom_file_path(patient_id, filename)
        ds = pydicom.dcmread(file_path)
        metadata = {}
        for elem in ds:
            if elem.name != "Pixel Data":
                metadata[elem.name] = str(elem.value)
        return JSONResponse(metadata)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="DICOM file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading DICOM file: {str(e)}")

@router.get("/{patient_id}/{filename}")
async def get_dicom_file(patient_id: str, filename: str):
    """Получение DICOM файла для конкретного пациента."""
    try:
        file_path = dicom_service.get_dicom_file_path(patient_id, filename)
        return FileResponse(file_path, media_type="application/dicom")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="DICOM file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))