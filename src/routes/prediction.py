from fastapi import APIRouter, Depends, UploadFile, File
from ..services.prediction_service import provide_prediction_test

router = APIRouter()

@router.post("/prediction/test")
async def prediction_test(file: UploadFile):
    return await provide_prediction_test(file)