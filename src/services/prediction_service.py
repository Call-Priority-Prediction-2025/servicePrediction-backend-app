from fastapi import UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import datetime
from ..response.success_response import SuccessResponse
from ..schema.input_prediction import InputPrediction
from ..errors.custom_error import CustomError
from ..config.config import get_config
from ..utils.prediction_util.encode_information import (
    get_city_encoded,
    get_region_encoded,
    get_day_encoded,
    get_occupation_encoded,
    get_encoded_datetime,
    get_encoded_maritalStatus,
)
from dotenv import load_dotenv

import pandas as pd
import json
import os
import traceback
import pickle

load_dotenv()


# config = get_config()
SELECTED_MODEL = os.environ["SELECTED_MODEL_PREDICTOR"]


# Services Functions ---
async def provide_prediction_test(
    file: UploadFile = File(...), selected_model: str = Form(...)
):
    try:
        # pengecekan ektensi file yang diizinkan (.csv, .xlsx, .json)
        check_extension(file)
        # penanganan dan pengubahan dari file input menjadi dict
        mandatory_columns = [
            "start_time",
            "age",
            "domicile",
            "occupation",
            "marital_status",
            "monthly_salary",
            "depend_child",
            "tenor",
        ]
        input_json = handle_file_to_dict(file, mandatory_columns)

        model_path = os.path.join(
            os.path.dirname(__file__), "..", "predictor", selected_model
        )
        with open(model_path, "rb") as f:
            model_predictor = pickle.load(f)

        result_json = []
        for eachData in input_json:
            # preprocessing
            input_predict = preprocess(eachData)
            input_dataframe = pd.DataFrame(input_predict)
            # prediksi
            prediction = model_predictor.predict(input_dataframe)
            prediction_probability = model_predictor.predict_proba(input_dataframe)
            # hasil
            result_json.append(
                {**eachData, "probability_rejected_call": prediction_probability[0][0]}
            )

        # mengurutkan hasil prediksi berdarsarkan nilai probabilitas (ascending)
        sorted_result_json = sorted(
            result_json, key=lambda x: x["probability_rejected_call"], reverse=False
        )

        return {"result": sorted_result_json}

    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_prediction(file: UploadFile = File(...)):
    try:
        # pengecekan ektensi file yang diizinkan (.csv, .xlsx, .json)
        check_extension(file)
        # penanganan dan pengubahan dari file input menjadi dict
        mandatory_columns = [
            "start_time",
            "age",
            "city_domicile",
            "occupation",
            "marital_status",
            "monthly_salary",
            "depend_child",
            "tenor",
        ]
        input_json = handle_file_to_dict(file, mandatory_columns)

        print("testing model selected env: ", SELECTED_MODEL)

        model_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "storage",
            "predictors",
            SELECTED_MODEL,
        )

        with open(model_path, "rb") as f:
            model_predictor = pickle.load(f)

        result_json = []
        for eachData in input_json:
            # preprocessing
            input_predict = preprocess(eachData)
            input_dataframe = pd.DataFrame(input_predict)

            # prediksi
            prediction = model_predictor.predict(input_dataframe)
            prediction_probability = model_predictor.predict_proba(input_dataframe)

            # hasil
            result_json.append(
                {
                    **eachData,
                    "probability_rejected_call": round(prediction_probability[0][0], 3),
                },
            )

        # mengurutkan hasil prediksi berdarsarkan nilai probabilitas (ascending)
        sorted_result_json = sorted(
            result_json, key=lambda x: x["probability_rejected_call"], reverse=False
        )

        for item in sorted_result_json:
            if isinstance(item["start_time"], pd.Timestamp):
                item["start_time"] = item["start_time"].strftime("%Y-%m-%d %H:%M:%S")

        return SuccessResponse(
            status_code=200, message="Prediction success", data=sorted_result_json
        )

    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_prediction_review(
    file: UploadFile = File(...), selected_model: str = Form(...)
):
    try:
        # pengecekan ektensi file yang diizinkan (.csv, .xlsx, .json)
        check_extension(file)
        # penanganan dan pengubahan dari file input menjadi dict
        mandatory_columns = [
            "start_time",
            "total_talk_time",
            "age",
            "city_domicile",
            "occupation",
            "marital_status",
            "monthly_salary",
            "depend_child",
            "tenor",
        ]
        input_json = handle_file_to_dict(file, mandatory_columns)

        model_path = os.path.join(
            os.path.dirname(__file__), "..", "storage", "predictors", selected_model
        )
        with open(model_path, "rb") as f:
            model_predictor = pickle.load(f)

        result_json = []
        for eachData in input_json:
            # preprocessing
            input_predict = preprocess_review(eachData)
            input_dataframe = pd.DataFrame(input_predict)
            # prediksi
            prediction = model_predictor.predict(input_dataframe)
            prediction_probability = model_predictor.predict_proba(input_dataframe)
            # hasil
            result_json.append(
                {
                    **eachData,
                    "probability_rejected_call": round(prediction_probability[0][0], 3),
                    "probability_accepted_call": round(prediction_probability[0][1], 3),
                    "previous_status": 1 if eachData["total_talk_time"] > 0 else 0,
                    "predicted_status": prediction[0],
                    "conclusion_predict": (
                        "correct"
                        if prediction_probability[0][0] > prediction_probability[0][1]
                        and eachData["total_talk_time"] == 0
                        or prediction_probability[0][0] < prediction_probability[0][1]
                        and eachData["total_talk_time"] > 0
                        else "wrong"
                    ),
                },
            )

        # mengurutkan hasil prediksi berdarsarkan nilai probabilitas (ascending)
        sorted_result_json = sorted(
            result_json, key=lambda x: x["probability_rejected_call"], reverse=False
        )

        # total data yang diinput
        total_data = len(input_json)
        # prediksi benar keseluruhan
        total_correct = len(
            [x for x in result_json if x["conclusion_predict"] == "correct"]
        )
        # prediksi salah keseluruhan
        total_wrong = len(
            [x for x in result_json if x["conclusion_predict"] == "wrong"]
        )

        # total data berlabel 1
        total_data_label_1 = len([x for x in result_json if x["previous_status"] == 1])
        # prediksi benar keseluruhan label 1
        total_correct_label_1 = len(
            [
                x
                for x in result_json
                if x["conclusion_predict"] == "correct" and x["previous_status"] == 1
            ]
        )
        # prediksi salah keseluruhan label 1
        total_wrong_label_1 = len(
            [
                x
                for x in result_json
                if x["conclusion_predict"] == "wrong" and x["previous_status"] == 1
            ]
        )

        # total data berlabel 0
        total_data_label_0 = len([x for x in result_json if x["previous_status"] == 0])
        # prediksi benar keseluruhan label 0
        total_correct_label_0 = len(
            [
                x
                for x in result_json
                if x["conclusion_predict"] == "correct" and x["previous_status"] == 0
            ]
        )
        # prediksi salah keseluruhan label 0
        total_wrong_label_0 = len(
            [
                x
                for x in result_json
                if x["conclusion_predict"] == "wrong" and x["previous_status"] == 0
            ]
        )

        return SuccessResponse(
            status_code=status.HTTP_200_OK,
            message="Success prediction",
            data={
                "review_result": {
                    "total_data": total_data,
                    "total_correct": total_correct,
                    "total_wrong": total_wrong,
                    "total_data_label_1": total_data_label_1,
                    "total_correct_label_1": total_correct_label_1,
                    "total_wrong_label_1": total_wrong_label_1,
                    "total_data_label_0": total_data_label_0,
                    "total_correct_label_0": total_correct_label_0,
                    "total_wrong_label_0": total_wrong_label_0,
                },
                "sorted_result_prediction": sorted_result_json,
            },
        )

    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_prediction_compare(
    validation_file: UploadFile = File(...), model_to_compare: str = Form(...)
):
    try:
        check_extension(validation_file)
        # penanganan dan pengubahan dari file input menjadi dict
        mandatory_columns = [
            "start_time",
            "age",
            "city_domicile",
            "occupation",
            "marital_status",
            "monthly_salary",
            "depend_child",
            "tenor",
        ]
        input_json = handle_file_to_dict(validation_file, mandatory_columns)
        model_path = os.path.join(
            os.path.dirname(__file__), "..", "storage", "predictors", model_to_compare
        )
        with open(model_path, "rb") as f:
            model_predictor = pickle.load(f)
        result_json = []
        for eachData in input_json:
            # preprocessing
            input_predict = preprocess_review(eachData)
            input_dataframe = pd.DataFrame(input_predict)
            # prediksi
            prediction = model_predictor.predict(input_dataframe)
            prediction_probability = model_predictor.predict_proba(input_dataframe)
            # hasil
            result_json.append(
                {
                    **eachData,
                    "probability_rejected_call": round(prediction_probability[0][0], 3),
                    "probability_accepted_call": round(prediction_probability[0][1], 3),
                    "previous_status": 1 if eachData["total_talk_time"] > 0 else 0,
                    "conclusion_predict": (
                        "correct"
                        if prediction_probability[0][0] > prediction_probability[0][1]
                        and eachData["total_talk_time"] == 0
                        or prediction_probability[0][0] < prediction_probability[0][1]
                        and eachData["total_talk_time"] > 0
                        else "wrong"
                    ),
                },
            )

        # prediksi benar keseluruhan
        total_correct = len(
            [x for x in result_json if x["conclusion_predict"] == "correct"]
        )

        return SuccessResponse(
            status_code=status.HTTP_200_OK,
            message="Success prediction",
            data={"score_total_correct": total_correct, "model_name": model_to_compare},
        )

    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")


async def provide_get_models():
    try:
        folder_predictor_path = Path(__file__).parent.parent / "predictor"
        if not folder_predictor_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Internal server error: folder predictor not found",
            )

        files = []
        for file in folder_predictor_path.iterdir():
            if file.is_file() and file.suffix == ".pkl":
                file_stat = file.stat()
                files.append(
                    {
                        "name": file.name,
                        "size": file_stat.st_size,
                        "last_modified": datetime.fromtimestamp(
                            file_stat.st_mtime
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
        return files
    except Exception as e:
        if isinstance(e, CustomError):
            raise e
        else:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")


# Tools Functions ---
def preprocess_review(data):
    try:
        start_time = str(data["start_time"])
        age = data["age"]
        region = data["city_domicile"].split(" ")[0]
        city = data["city_domicile"].split(" ")[1]
        occupation = data["occupation"]
        marital_status = data["marital_status"]
        monthly_salary = data["monthly_salary"]
        tanggungan = data["depend_child"]
        tenor = data["tenor"]

        # data encoded
        region_encoded = get_region_encoded(region)
        city_encoded = get_city_encoded(city)
        occupation_encoded = get_occupation_encoded(occupation)
        day_name, time_in_seconds = get_encoded_datetime(start_time)
        day_encoded = get_day_encoded(day_name)
        marital_status_encoded = get_encoded_maritalStatus(marital_status)

        input_predict = {
            "age": [age],
            "monthly_salary": [monthly_salary],
            "depend_child": [tanggungan],
            "tenor": [tenor],
            "time_second": [time_in_seconds],
            "region_encoded": [region_encoded],
            "day_name_encoded": [day_encoded],
            "city_encoded": [city_encoded],
            "marital_status_encoded": [marital_status_encoded],
            "occupation_encoded": [occupation_encoded],
        }
        return input_predict

    except Exception as e:
        print(traceback.format_exc())
        raise CustomError(status_code=500, detail="error while preprocessing")


def preprocess(data):
    try:
        # data original
        age = data["age"]
        region = data["city_domicile"].split(" ")[0]
        city_domicile = data["city_domicile"].split(" ")[1]
        occupation = data["occupation"]
        marital_status = data["marital_status"]
        start_time = str(data["start_time"])

        # data encoded
        region_encoded = get_region_encoded(region)
        city_encoded = get_city_encoded(city_domicile)
        occupation_encoded = get_occupation_encoded(occupation)
        day_name, time_in_seconds = get_encoded_datetime(start_time)
        day_encoded = get_day_encoded(day_name)
        marital_status_encoded = get_encoded_maritalStatus(marital_status)

        input_predict = {
            "age": [age],
            "monthly_salary": [data["monthly_salary"]],
            "depend_child": [data["depend_child"]],
            "tenor": [data["tenor"]],
            "time_second": [time_in_seconds],
            "region_encoded": [region_encoded],
            "day_name_encoded": [day_encoded],
            "city_encoded": [city_encoded],
            "marital_status_encoded": [marital_status_encoded],
            "occupation_encoded": [occupation_encoded],
        }

        return input_predict
    except Exception as e:
        print(traceback.format_exc())
        raise CustomError(status_code=500, detail="error while preprocessing")


def check_extension(file: UploadFile):
    if file.filename.endswith(".csv"):
        return True
    elif file.filename.endswith(".xlsx"):
        return True
    elif file.filename.endswith(".json"):
        return True
    else:
        raise CustomError(status_code=400, detail="Unpermitted file extension")


def handle_file_to_dict(file: UploadFile, mandatory_columns: list):
    if file.filename.endswith(".csv"):
        input_file = pd.read_csv(file.file, delimiter="\t")
        # mengecek kolom yang dibutuhkan
        if not set(mandatory_columns).issubset(set(input_file.columns)):
            raise CustomError(status_code=400, detail="Missing mandatory columns")
    elif file.filename.endswith(".xlsx"):
        input_file = pd.read_excel(file.file)
        print("kolom: ", input_file.columns)
        # mengecek kolom yang dibutuhkan
        if not set(mandatory_columns).issubset(set(input_file.columns)):
            raise CustomError(status_code=400, detail="Missing mandatory columns")
    elif file.filename.endswith(".json"):
        input_file = pd.read_json(file.file)
        # mengecek kolom yang dibutuhkan
        if not set(mandatory_columns).issubset(set(input_file.columns)):
            raise CustomError(status_code=400, detail="Missing mandatory columns")

    file_to_dict = input_file.to_dict(orient="records")
    return file_to_dict
