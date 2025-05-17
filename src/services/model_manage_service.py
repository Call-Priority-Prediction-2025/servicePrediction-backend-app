from fastapi import Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session, joinedload, join
from sqlalchemy.sql import select
from typing import Annotated
from datetime import datetime
from dotenv import load_dotenv, set_key
from ..schema import schemas
from ..models import models
from ..response.success_response import SuccessResponse
from ..errors.custom_error import CustomError
from ..schema import schemas
from .auth_service import get_current_user
import traceback
import os


async def provide_add_model(
    db: Session, new_modelPred: UploadFile = File(...), uploader_id: str = Form(...)
):
    try:
        extension_file = new_modelPred.filename.split(".")[-1]
        if extension_file not in ["pkl", "pickle"]:
            raise CustomError(status_code=400, detail="Unpermitted file extension")

        existed_filename = (
            db.query(models.ModelPredictor)
            .filter(models.ModelPredictor.file_model_name == new_modelPred.filename)
            .first()
        )
        if existed_filename:
            raise CustomError(
                status_code=400, detail="duplicate file name or file already exist"
            )

        storage_folder_path = os.path.join(
            os.path.dirname(__file__), "..", "storage", "predictors"
        )
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
            file_model_name=new_modelPred.filename,
            uploaded_by=int(uploader_id),
            updated_by=int(uploader_id),
            uploaded_at=current_time,
        )
        db.add(db_modelPred)
        db.commit()
        db.refresh(db_modelPred)

        return SuccessResponse(
            status_code=status.HTTP_201_CREATED,
            message="Model added successfully",
            data={},
        )
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_get_modelPredictor_detail(db: Session, model_id: str):
    try:
        model_predictor = db.query(models.ModelPredictor).filter_by(id=model_id).first()
        if model_predictor is None:
            raise CustomError(code=404, message="Model not found")

        return SuccessResponse(
            status_code=status.HTTP_200_OK,
            message="Success get model",
            data=model_predictor.to_dict(),
        )
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_get_modelPredictors(db: Session):
    try:
        model_predictors = db.query(models.ModelPredictor).all()
        result_model_predictors = []
        for model_pred in model_predictors:
            model_pred_dict = model_pred.to_dict()

            if model_pred.updated_by is not None:
                query_statement = select(models.User.username).where(
                    models.User.id == model_pred.updated_by
                )
                result = db.execute(query_statement).scalar()
                get_updated_by = result

            model_pred_dict["updated_by"] = get_updated_by
            result_model_predictors.append(model_pred_dict)

        founded_files_predictors = []
        folder_model_predictors = os.path.join(
            os.path.dirname(__file__), "..", "storage", "predictors"
        )
        for file in os.listdir(folder_model_predictors):
            if os.path.isfile(
                os.path.join(folder_model_predictors, file)
            ):  # Memastikan bahwa ini adalah file, bukan folder
                founded_files_predictors.append(file)

        valid_model_predictors = []
        for model_predictor in result_model_predictors:
            if model_predictor["file_model_name"] in founded_files_predictors:
                valid_model_predictors.append(model_predictor)

        return SuccessResponse(
            status_code=status.HTTP_200_OK,
            message="success retrieve model predictors",
            data=valid_model_predictors,
        )
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_update_model(
    db: Session, model_id: str, updater_id: str, new_modelPred: UploadFile = File(...)
):
    try:
        extension_file = new_modelPred.filename.split(".")[-1]
        if extension_file not in ["pkl", "pickle"]:
            raise CustomError(status_code=400, detail="Unpermitted file extension")

        existed_data = db.query(models.ModelPredictor).filter_by(id=model_id).first()
        if not existed_data:
            raise CustomError(status_code=404, detail="Data model predictor not found")

        existed_filename = (
            db.query(models.ModelPredictor)
            .filter(models.ModelPredictor.file_model_name == new_modelPred.filename)
            .first()
        )
        if existed_filename:
            raise CustomError(
                status_code=400, detail="duplicate file name or file already exist"
            )

        storage_folder_path = os.path.join(
            os.path.dirname(__file__), "..", "storage", "predictors"
        )

        # Hapus file lama
        file_location = os.path.join(storage_folder_path, existed_data.file_model_name)
        if not os.path.exists(file_location):
            raise CustomError(status_code=404, detail="File model predictor not found")
        os.remove(file_location)

        # Upload file baru
        file_location_newModel = os.path.join(
            storage_folder_path, new_modelPred.filename
        )
        with open(file_location_newModel, "wb") as file_object:
            file_object.write(new_modelPred.file.read())
            print("INFO: file uploaded successfully")

        # Update data nama file model di database
        existed_data.file_model_name = new_modelPred.filename
        existed_data.updated_by = updater_id
        existed_data.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.commit()
        db.refresh(existed_data)

        return SuccessResponse(
            status_code=200, message="Model updated successfully", data=[]
        )
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_delete_model(db: Session, model_id: str):
    try:
        existed_data = db.query(models.ModelPredictor).filter_by(id=model_id).first()
        if not existed_data:
            raise CustomError(status_code=404, detail="Data model predictor not found")

        storage_folder_path = os.path.join(
            os.path.dirname(__file__), "..", "storage", "predictors"
        )
        file_location = os.path.join(storage_folder_path, existed_data.file_model_name)
        if not os.path.exists(file_location):
            raise CustomError(status_code=404, detail="File model predictor not found")
        os.remove(file_location)

        db.delete(existed_data)
        db.commit()
        return SuccessResponse(
            status_code=200, message="Model deleted successfully", data=[]
        )
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_set_system_predictor(model_selection: str):
    try:
        print(model_selection)
        storage_folder_path = os.path.join(
            os.path.dirname(__file__), "..", "storage", "predictors"
        )
        if not os.path.exists(storage_folder_path):
            raise HTTPException(
                status_code=404, detail=f"Model dengan nama {model_selection} not found"
            )

        load_dotenv("../../.env")
        set_key("SELECTED_MODEL_PREDICTOR", model_selection)

        # Reload environment variables setelah update
        load_dotenv(dotenv_path=".env", override=True)

        return SuccessResponse(
            status_code=200,
            message="Model deleted successfully",
            data={"selected_system_model": model_selection},
        )
    except Exception as e:
        if isinstance(e, CustomError):
            print(traceback.format_exc())
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")
