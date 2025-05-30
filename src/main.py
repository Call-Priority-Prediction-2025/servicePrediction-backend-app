from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from .errors.custom_error import CustomError
from .routes.auth import router as auth_router
from .routes.prediction import router as prediction_router
from .routes.model_manage import router as model_manage_router
from .routes.user_manage import router as user_manage_router
from .database import Base, engine
from .models import models
from sqlalchemy.orm import Session
from typing import Annotated
from .schema.types import ModelPredictor_type
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(prediction_router, prefix="/api")
app.include_router(model_manage_router, prefix="/api")
app.include_router(user_manage_router, prefix="/api")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        },
    )


@app.exception_handler(CustomError)
async def custo_exception_handler(request: Request, exc: CustomError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "CustomHTTPException",
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        },
    )


@app.get("/")
async def root_route():
    return {"message": "API run properly"}


# @app.post("/testing/add-model", status_code=status.HTTP_201_CREATED)
# async def add_model(model: ModelPredictor_type, db: db_dependency):
#     db_model = models.ModelPredictor(**model.dict())
#     db.add(db_model)
#     db.commit()
