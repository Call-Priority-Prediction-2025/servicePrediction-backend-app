from sqlalchemy import (
    Boolean,
    String,
    Column,
    Integer,
    String,
    TIMESTAMP,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from ..database import Base
from ..schema.schemas import RoleEnum


class ModelPredictor(Base):
    __tablename__ = "model_predictors"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    file_model_name = Column(String(50), index=True, unique=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), index=True)
    updated_by = Column(Integer, index=True, nullable=True)
    uploaded_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)

    uploader = relationship("User", back_populates="model_predictors")

    def to_dict(self):
        return {
            "id": self.id,
            "file_model_name": self.file_model_name,
            "uploaded_by": self.uploader.username,
            "uploaded_at": (
                self.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.uploaded_at
                else None
            ),
            "updated_at": (
                self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                if self.updated_at
                else None
            ),
        }


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    usercode = Column(String(50), index=True, unique=True)
    username = Column(String(50), index=True)
    role = Column(SQLEnum(RoleEnum), index=True)
    password = Column(String(255), index=True)

    model_predictors = relationship("ModelPredictor", back_populates="uploader")

    def to_dict(self):
        return {
            "id": self.id,
            "usercode": self.usercode,
            "username": self.username,
            "role": self.role.value,
        }
