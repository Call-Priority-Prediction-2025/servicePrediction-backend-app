import os 
import json
import pandas as pd
import locale
from datetime import datetime
from ...schema.types import InputTime

def get_city_encoded(input_city): 
    # mengimport file city_information.json
    city_information_path = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "prediction_information", "city_information.json")
    with open(city_information_path) as f:
        city_information = json.load(f)

    # mencari nilai encode yang ada di file city_information.json
    encode_value = None
    for eachCity in city_information:
        if eachCity["city"] == input_city:
            encode_value = eachCity["encode"]
            break
    
    return encode_value

def get_occupation_encoded(input_occupation):
    # mengimport file region_information.json
    occupation_information_path = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "prediction_information", "occupation_information.json")   
    with open(occupation_information_path) as f:    
        occupation_information = json.load(f)

    # mencari nilai encode yang ada di file city_information.json
    encode_value = None
    for eachOccupation in occupation_information:
        if eachOccupation["occupation"] == input_occupation:
            encode_value = eachOccupation["encode"]
            break
    
    return encode_value

def get_region_encoded(input_region):
    # mengimport file region_information.json
    region_information_path = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "prediction_information", "region_information.json")   
    with open(region_information_path) as f:    
        region_information = json.load(f)

    # mencari nilai encode yang ada di file city_information.json
    encode_value = None
    for eachRegion in region_information:
        if eachRegion["region"] == input_region:
            encode_value = eachRegion["encode"]
            break
    
    return encode_value

def get_day_encoded(input_day):
    # mengimport file region_information.json
    day_information_path = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "prediction_information", "day_information.json")   
    with open(day_information_path) as f:    
        day_information = json.load(f)

    # mencari nilai encode yang ada di file city_information.json
    encode_value = None
    for eachDay in day_information:
        if eachDay["day_name"] == input_day:
            encode_value = eachDay["encode"]
            break
    
    return encode_value

def get_encoded_datetime(input_datetime):
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

        # konversi string ke datetime
        datetime_coverted = datetime.strptime(input_datetime, '%Y-%m-%d %H:%M:%S')
        date_part = datetime_coverted.date()
        time_part = datetime_coverted.time()

        day_name = date_part.strftime("%A")
        time_converted_seconds = time_to_seconds(time_part)

        return day_name, time_converted_seconds

def time_to_seconds(input_time):
    h = input_time.hour
    m = input_time.minute
    s = input_time.second

    total_seconds = h * 3600 + m * 60 + s
    return total_seconds