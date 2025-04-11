import logging

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import dicom_endpoints, router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(dicom_endpoints.router, tags=["DICOM"])
app.include_router(router.router, tags=["DICOM"])