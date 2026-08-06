from fastapi import APIRouter
from app.api.v1 import auth, employees, learning, simulations, quizzes, knowledge, recommendation

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(learning.router, prefix="/learning", tags=["curriculum"])
api_router.include_router(simulations.router, prefix="/simulations", tags=["simulations"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge-base"])
api_router.include_router(recommendation.router, prefix="/recommendations", tags=["recommendations"])
