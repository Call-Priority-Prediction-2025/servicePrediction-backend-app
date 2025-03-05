from fastapi import Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime
from ..schema import schemas
from ..models import models
from ..response.success_response import SuccessResponse
from ..errors.custom_error import CustomError
from ..schema import schemas
import traceback
import os

async def provide_add_model(db: Session, new_modelPred: UploadFile = File(...), uploader_id: str = Form(...)):
     try:
        extension_file = new_modelPred.filename.split(".")[-1]
        if extension_file not in ["pkl", "pickle"]:
            raise CustomError(status_code=400, detail="Unpermitted file extension")
        
        existed_filename = db.query(models.ModelPredictor).filter(models.ModelPredictor.file_model_name == new_modelPred.filename).first()
        if existed_filename:
            raise CustomError(status_code=400, detail="duplicate file name or file already exist")

        storage_folder_path = os.path.join(os.path.dirname(__file__), "..", "storage", "predictors")
        if not os.path.exists(storage_folder_path):
            os.makedirs(storage_folder_path)
        
        file_location = os.path.join(storage_folder_path, new_modelPred.filename)
        try: 
            with open(file_location, "wb") as file_object: 
                file_object.write(new_modelPred.file.read())
            print("INFO: file uploaded successfully")
        except Exception as e:
            raise CustomError(status_code=500, detail="error while uploading file")

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db_modelPred = models.ModelPredictor(
            file_model_name = new_modelPred.filename,
            uploaded_by = int(uploader_id),
            updated_by = int(uploader_id),
            uploaded_at = current_time,
        )
        db.add(db_modelPred)
        db.commit()
        db.refresh(db_modelPred)

        return SuccessResponse(status_code=201, message="Model added successfully", data={})
     except Exception as e:
          if isinstance(e, CustomError):
            raise e
          else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")
          

async def provide_get_modelPredictors(db: Session):
    try:
        model_predictors = db.query(models.ModelPredictor).all()
        model_predictors = [model_pred.to_dict() for model_pred in model_predictors]

        founded_files_predictors = []
        folder_model_predictors = os.path.join(os.path.dirname(__file__), "..", "storage", "predictors")
        for file in os.listdir(folder_model_predictors):
            if os.path.isfile(os.path.join(folder_model_predictors, file)):  # Memastikan bahwa ini adalah file, bukan folder
                founded_files_predictors.append(file)
        
        valid_model_predictors = []
        for model_predictor in model_predictors:
            if model_predictor["file_model_name"] in founded_files_predictors:
                valid_model_predictors.append(model_predictor)

        return SuccessResponse(status_code=200, message="success retrieve model predictors", data=valid_model_predictors)
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")
     