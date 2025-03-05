from fastapi.responses import JSONResponse

class SuccessResponse(JSONResponse):
    def __init__(self, status_code: int, message: str, data:list):
        super().__init__(status_code=status_code, content={
            "status_code": status_code,
            "message": message,
            "data": data
        })