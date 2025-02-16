from fastapi import APIRouter, Depends
from ..services.auth_service import provide_login

router = APIRouter()

@router.get("/login")
async def login():
    return await provide_login()