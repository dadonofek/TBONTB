"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "TBONTB API"

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:8000",  # FastAPI dev server
        "https://tbontb.vercel.app",  # Production frontend (update with your domain)
    ]

    # Simulation Settings
    DEFAULT_SIMULATION_YEARS: int = 30
    DEFAULT_N_SIMULATIONS: int = 10000
    MAX_N_SIMULATIONS: int = 50000

    # Tax Settings
    DEFAULT_STOCKS_TAX_RATE: float = 25.0

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
