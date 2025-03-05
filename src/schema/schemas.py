from pydantic import BaseModel, Field
from datetime import datetime

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
