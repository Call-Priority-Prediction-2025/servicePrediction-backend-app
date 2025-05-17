from fastapi import HTTPException, Form, status
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import select, alias
from passlib.context import CryptContext
from ..schema.schemas import CreateUserRequest, UpdateUserRequest
from ..response.success_response import SuccessResponse
from ..errors.custom_error import CustomError
from ..models import models

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def provide_create_user(db: Session, create_user_request: CreateUserRequest):
    try:

        if create_user_request.password != create_user_request.confirm_password:
            raise CustomError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirm password not match",
            )

        existed_user = (
            db.query(models.User)
            .filter_by(usercode=create_user_request.usercode)
            .first()
        )
        if existed_user:
            raise CustomError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User code already exist",
            )

        new_user = models.User(
            usercode=create_user_request.usercode,
            username=create_user_request.username,
            role=create_user_request.role,
            password=bcrypt_context.hash(create_user_request.password),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return SuccessResponse(
            status_code=201, message="User created successfully", data=[]
        )
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(e)
            print(create_user_request)
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_get_users(db: Session):
    try:
        users = db.query(models.User).all()
        users = [user.to_dict() for user in users]

        return SuccessResponse(
            status_code=status.HTTP_200_OK, message="Success retrieve users", data=users
        )
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )


async def provide_get_detail_user(db: Session, user_id: str):
    try:
        existed_user = db.query(models.User).filter_by(id=user_id).first()
        if not existed_user:
            raise CustomError(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return SuccessResponse(
            status_code=status.HTTP_200_OK,
            message="Success retrieve user",
            data=existed_user.to_dict(),
        )
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )


async def provide_update_user(
    db: Session, user_id: str, auth_user: dict, form_update: UpdateUserRequest
):
    try:
        existed_user = db.query(models.User).filter_by(id=user_id).first()
        if not existed_user:
            raise CustomError(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        existed_user.username = (
            form_update.username
            if form_update.username is not None
            else existed_user.username
        )
        existed_user.role = (
            form_update.role if form_update.role is not None else existed_user.role
        )

        new_password = None
        if form_update.password is not None:
            if form_update.password != form_update.confirm_password:
                raise CustomError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Confirm password not match",
                )
            new_password = bcrypt_context.hash(form_update.password)

        existed_user.password = (
            new_password if new_password is not None else existed_user.password
        )

        db.commit()
        db.refresh(existed_user)

        return SuccessResponse(
            status_code=status.HTTP_200_OK, message="User updated successfully", data=[]
        )
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )


async def provide_delete_user(db: Session, user_id: str):
    try:
        existed_user = db.query(models.User).filter_by(id=user_id).first()
        if not existed_user:
            raise CustomError(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Mengecek apakah masih ada user yang berelasi dengan tabel model predictor
        mp1 = aliased(models.ModelPredictor)
        mp2 = aliased(models.ModelPredictor)
        query_statement = (
            select(models.User.usercode)
            .join(
                mp1,
                mp1.uploaded_by == models.User.id,
            )
            .join(
                mp2,
                mp2.updated_by == models.User.id,
            )
            .where(models.User.id == user_id)
        )
        joined_modelPredicts = db.execute(query_statement).all()
        if len(joined_modelPredicts) > 0:
            raise CustomError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User still related to model predicts",
            )

        db.delete(existed_user)
        db.commit()

        return SuccessResponse(
            status_code=status.HTTP_200_OK, message="Success delete user", data=[]
        )
    except Exception as e:
        print(e)
        if isinstance(e, CustomError):
            raise e
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
