from fastapi import APIRouter, Depends, status, Form, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from ..database import SessionLocal
from ..schema.schemas import CreateUserRequest, UpdateUserRequest
from ..services import user_manage_service as service
from ..models import models
from ..response.success_response import SuccessResponse
from ..errors.custom_error import CustomError
from ..services.auth_service import get_current_user, require_admin

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/user-manage/create")
async def create_user(
    create_user_request: CreateUserRequest,
    db: Session = Depends(get_db),
    auth_user: dict = Depends(require_admin),
):
    return await service.provide_create_user(db, create_user_request)


@router.get("/user-manage/{user_id}/detail-user")
async def get_detail_user(
    user_id: str,
    db: Session = Depends(get_db),
    auth_user: dict = Depends(require_admin),
):
    return await service.provide_get_detail_user(user_id=user_id, db=db)


@router.get("/user-manage/users")
async def get_users(
    db: Session = Depends(get_db), auth_user: dict = Depends(require_admin)
):
    return await service.provide_get_users(db=db)


@router.put("/user-manage/{user_id}/update-user")
async def update_user(
    user_id: str,
    form_update: UpdateUserRequest,
    db: Session = Depends(get_db),
    auth_user: dict = Depends(require_admin),
):
    return await service.provide_update_user(
        user_id=user_id, db=db, auth_user=auth_user, form_update=form_update
    )


@router.delete("/user-manage/{user_id}/delete-user")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    auth_user: dict = Depends(require_admin),
):
    return await service.provide_delete_user(db=db, user_id=user_id)
