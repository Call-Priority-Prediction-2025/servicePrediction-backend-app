from fastapi import APIRouter, Depends, Form, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Annotated
from ..database import SessionLocal
from ..schema import schemas
from ..services.model_manage_service import provide_add_model, provide_get_modelPredictors

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/model-manage/add-model", status_code=status.HTTP_201_CREATED)
async def add_model(new_modelPred: UploadFile = File(...), uploader_id: str = Form(...), db: Session = Depends(get_db)):
    return await provide_add_model(db=db, new_modelPred=new_modelPred, uploader_id=uploader_id)

@router.get("/model-manage/models", status_code=status.HTTP_200_OK)
async def get_models(db: Session = Depends(get_db)):
    return await provide_get_modelPredictors(db=db)