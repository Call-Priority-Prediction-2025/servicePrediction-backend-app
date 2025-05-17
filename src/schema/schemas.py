from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ModelPredictorBase(BaseModel):
    file_model_name: str
    uploaded_by: int
    updated_by: int = Field(default_factory=lambda: None)
    uploaded_at: str | None = Field(default_factory=lambda: None)
    updated_at: str | None = Field(default_factory=lambda: None)


class ModelPredictorCreate(ModelPredictorBase):
    pass


class ModelPredictor(ModelPredictorBase):
    id: int

    class Config:
        from_attributes = True


class CreateUserRequest(BaseModel):
    usercode: str = Field(..., min_length=1, description="User code")
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., min_length=8, description="Confirm password")
    role: str = Field(default="user", description="Role")


class UserBase(BaseModel):
    id: int
    usercode: str
    username: str
    role: str
    password: str


class Users(BaseModel):
    id: int
    usercode: str
    username: str
    role: str


class UserLoginRequest(BaseModel):
    usercode: str
    password: str


class UpdateUserRequest(BaseModel):
    username: str | None = Field(default_factory=lambda: None)
    role: str | None = Field(default_factory=lambda: None)
    password: str | None = Field(default_factory=lambda: None)
    confirm_password: str | None = Field(default_factory=lambda: None)


class Token(BaseModel):
    access_token: str
    token_type: str


class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"

# Model untuk request
class ModelSelection(BaseModel):
    model_name: str