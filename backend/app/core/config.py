import os
from pathlib import Path
from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bosch AI-Powered Personalized Learning Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretjwtkeyforboschaiplp2026!!!"  # In prod, load from env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "aiplp"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: str = "sqlite+aiosqlite:///../aiplp.db"


    # Gemini
    GEMINI_API_KEY: str = ""

    # MATLAB MCP Server Configuration
    MATLAB_MCP_COMMAND: str = "npx -y @modelcontextprotocol/server-matlab" # Command to start MATLAB MCP server
    
    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    SIMULATION_DIR: Path = BASE_DIR / "data" / "simulations"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.SIMULATION_DIR, exist_ok=True)
