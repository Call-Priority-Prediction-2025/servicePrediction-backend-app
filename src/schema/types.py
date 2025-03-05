from pydantic import BaseModel

class InputTime(BaseModel):
    hour: int
    minute: int
    second: int

class ModelPredictor_type(BaseModel): 
    file_model_name: str
    uploaded_by: int
    updated_by: int
    uploaded_at: str
    updated_at: str
    