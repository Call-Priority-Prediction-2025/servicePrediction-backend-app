from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from ..services.auth_service import provide_login, get_current_user, provide_login_2
from ..database import SessionLocal
from ..schema import schemas
from ..errors.custom_error import CustomError
from ..response.success_response import SuccessResponse

SECRET_KEY = "ilhamyudantyo18092001"
ALGORITHM = "HS256"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="api/login")


@router.post("/login")
async def login(form_login: schemas.UserLoginRequest, db: Session = Depends(get_db)):
    return await provide_login(db=db, form_login=form_login)


@router.get("/verify-token")
async def verify_token(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token mandatory",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"status_code": status.HTTP_200_OK, "message": "token valid"}
    except JWTError:
        raise CustomError(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
        )
