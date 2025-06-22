from fastapi import APIRouter
from .endpoint_simulate import router as simulate_router
from .oas_calculator import router as oas_calculator_router

api_router = APIRouter()
api_router.include_router(simulate_router)
api_router.include_router(oas_calculator_router)
