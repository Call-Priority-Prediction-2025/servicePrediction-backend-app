from fastapi import FastAPI
from .routes.auth import router as auth_router
from .routes.prediction import router as prediction_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(prediction_router)

@app.get("/")
async def root_route(): 
    return {"message":"API run properly"}
