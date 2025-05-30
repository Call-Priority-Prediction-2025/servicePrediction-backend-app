from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from passlib.context import CryptContext
from jose import jwt, JWTError
from ..errors.custom_error import CustomError
from ..models import models
from ..schema import schemas
from ..response.success_response import SuccessResponse
from ..schema import schemas
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os
import json

load_dotenv()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="api/login")

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = os.environ["JWT_ALGORITHM"]
FERNET_KEY = os.environ['FERNET_KEY']

fernet = Fernet(FERNET_KEY)

async def provide_login(db: Session, form_login: schemas.UserLoginRequest):
    try:
        valid_user = authenticate_user(
            request_user_code=form_login.usercode,
            request_password=form_login.password,
            db=db,
        )

        access_token = create_access_token(
            data={
                "sub": valid_user.usercode,
                "username": valid_user.username,
                "user_id": valid_user.id,
                "user_role": valid_user.role,
            },
            expires_delta=timedelta(minutes=60),
        )

        return SuccessResponse(
            status_code=200,
            message="Login success",
            data={"access_token": access_token, "token_type": "bearer"},
        )
    except Exception as e:
        print(e)
        if isinstance(e, CustomError):
            raise e
        else:
            print(e)
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_login_2(db: Session, form_login: schemas.UserLoginRequest):
    try:
        valid_user = authenticate_user(
            request_user_code=form_login.usercode,
            request_password=form_login.password,
            db=db,
        )

        access_token = create_access_token_2(
            data={
                "sub": valid_user.usercode,
                "username": valid_user.username,
                "user_id": valid_user.id,
                "user_role": valid_user.role,
            },
            expires_delta=timedelta(minutes=60),
        )

        return SuccessResponse(
            status_code=200,
            message="Login success",
            data={"access_token": access_token, "token_type": "bearer"},
        )
    except Exception as e:
        print(e)
        if isinstance(e, CustomError):
            raise e
        else:
            print(e)
            raise HTTPException(status_code=500, detail="Internal server error")


def authenticate_user(
    request_user_code: str, request_password: str, db: Session
) -> models.User:
    existed_user = (
        db.query(models.User).filter(models.User.usercode == request_user_code).first()
    )

    if not existed_user:
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect usercode or password",
        )
    if not bcrypt_context.verify(request_password, existed_user.password):
        raise CustomError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect usercode or password",
        )

    return existed_user


def encrypt_payload_jwt(payload: dict)-> str:
    json_str = json.dumps(payload)
    encrypted = fernet.encrypt(json_str.encode())
    return encrypted.decode()


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expires = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token_2(data: dict, expires_delta: timedelta):
    encrypted_data = encrypt_payload_jwt(data)
    expires = datetime.utcnow() + expires_delta
    # to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(
        {"data":encrypted_data, "exp": expires}, 
        SECRET_KEY, 
        algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject_payload = payload.get("sub")

        if subject_payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token mandatory",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {
            "user_id": payload.get("user_id"),
            "user_name": payload.get("username"),
            "user_code": subject_payload,
            "user_role": payload.get("user_role"),
        }
    except JWTError:
        raise CustomError(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
        )


def require_admin(user: dict = Depends(get_current_user)):
    if user["user_role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin previlege required",
        )

    return user
