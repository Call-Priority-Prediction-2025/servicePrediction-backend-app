from fastapi import APIRouter, Depends, Form, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Annotated
from ..database import SessionLocal
from ..schema import schemas
from ..services.model_manage_service import (
    provide_add_model,
    provide_get_modelPredictors,
    provide_get_modelPredictor_detail,
    provide_update_model,
    provide_delete_model,
    provide_set_system_predictor,
)
from ..services.auth_service import get_current_user, require_admin

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/model-manage/add-model")
async def add_model(
    new_modelPred: UploadFile = File(...),
    uploader_id: str = Form(...),
    db: Session = Depends(get_db),
    auth_user: dict = Depends(require_admin),
):
    return await provide_add_model(
        db=db, new_modelPred=new_modelPred, uploader_id=uploader_id
    )


@router.get("/model-manage/models")
async def get_models(
    db: Session = Depends(get_db), auth_user: dict = Depends(require_admin)
):
    return await provide_get_modelPredictors(db=db)


@router.get("/model-manage/{model_id}/get-model")
async def get_model_detail(
    model_id: str,
    db: Session = Depends(get_db),
    auth_user: dict = Depends(require_admin),
):
    return await provide_get_modelPredictor_detail(db=db, model_id=model_id)


@router.put("/model-manage/{model_id}/update-model")
async def update_model(
    model_id: str,
    new_modelPred: UploadFile = File(...),
    updater_id: str = Form(...),
    db: Session = Depends(get_db),
    auth_user: dict = Depends(require_admin),
):
    return await provide_update_model(
        db=db, model_id=model_id, new_modelPred=new_modelPred, updater_id=updater_id
    )


@router.delete("/model-manage/{model_id}/delete-model")
async def delete_model(
    model_id: str,
    db: Session = Depends(get_db),
    auth_user: dict = Depends(require_admin),
):
    return await provide_delete_model(db=db, model_id=model_id)


@router.post("/model-manage/set-system-predictor")
async def set_system_predictor(
    model_selection: schemas.ModelSelection, auth_user: dict = Depends(require_admin)
):
    return await provide_set_system_predictor(model_selection.model_name)
