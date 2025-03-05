from pydantic import BaseModel
from typing import List

class InputPrediction(BaseModel):
   id: int
   start_time: str
   cust_name: str
   age: int
   domicile: str
   occupation: str
   marital_status: str
   monthly_salary: int
   tenor: int
   depend_child: int