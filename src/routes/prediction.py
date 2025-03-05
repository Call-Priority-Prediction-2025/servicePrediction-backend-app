from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from ..services.prediction_service import provide_prediction_test, provide_get_models, provide_prediction_review, provide_prediction

router = APIRouter()

@router.post("/prediction/test")
async def prediction_test(file: UploadFile = File(...), selected_model: str= Form(...)):
    return await provide_prediction_test(file, selected_model)

@router.post("/prediction")
async def prediction(file: UploadFile = File(...)):
    return await provide_prediction(file)

@router.post("/prediction/review")
async def prediction_review(file: UploadFile = File(...), selected_model: str= Form(...)):
    return await provide_prediction_review(file, selected_model)

@router.get("/prediction/models", status_code=status.HTTP_200_OK)
async def get_models():
    files = await provide_get_models()
    return {"models": files}