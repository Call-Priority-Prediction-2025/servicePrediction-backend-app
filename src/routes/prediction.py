from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from ..services.prediction_service import (
    provide_prediction_test,
    provide_get_models,
    provide_prediction_review,
    provide_prediction,
    provide_prediction_compare,
)
from ..services.auth_service import get_current_user, require_admin

router = APIRouter()


@router.post("/prediction/test")
async def prediction_test(
    file: UploadFile = File(...),
    selected_model: str = Form(...),
    auth_user: dict = Depends(get_current_user),
):
    return await provide_prediction_test(file, selected_model)


@router.post("/prediction")
async def prediction(
    file: UploadFile = File(...),
    auth_user: dict = Depends(get_current_user),
):
    return await provide_prediction(file)


@router.post("/prediction/review")
async def prediction_review(
    file: UploadFile = File(...),
    selected_model: str = Form(...),
    auth_user: dict = Depends(require_admin),
):
    return await provide_prediction_review(file, selected_model)


@router.post("/prediction/compare")
async def prediction_compare(
    validation_file: UploadFile = File(...),
    model_to_compare: str = Form(...),
    auth_user: dict = Depends(require_admin),
):
    return await provide_prediction_compare(validation_file, model_to_compare)


# deprecated
@router.get("/prediction/models")
async def get_models():
    files = await provide_get_models()
    return {"models": files}
