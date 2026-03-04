"""
Configuration management for Skill Match AI application.
Centralizes all constants, secrets, and environment variables.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""
    
    # API Configuration
    APP_NAME: str = "Skill Match AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database Configuration
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "skill_match_AI")
    MONGO_TIMEOUT_MS: int = 5000
    MONGO_CONNECT_TIMEOUT_MS: int = 10000
    
    # GitHub API Configuration
    GITHUB_API_KEY: str = os.getenv("GITHUB_API_KEY", "")
    GITHUB_API_BASE: str = "https://api.github.com"
    GITHUB_PER_PAGE: int = 100
    
    # Embedding Configuration
    EMBEDDING_MODEL_NAME: str = os.getenv(
        "EMBEDDING_MODEL_NAME", 
        "all-MiniLM-L6-v2"
    )
    
    # ML Model Configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "model.pkl")
    XGB_N_ESTIMATORS: int = 100
    XGB_MAX_DEPTH: int = 4
    XGB_LEARNING_RATE: float = 0.1
    
    # Feature Weights for Baseline Ranker
    WEIGHT_RESUME_SIM: float = 0.4
    WEIGHT_SKILLS_SIM: float = 0.3
    WEIGHT_GITHUB_SIM: float = 0.2
    WEIGHT_YEARS_EXP: float = 0.1
    MAX_YEARS_EXPERIENCE: int = 10
    
    # Section Confidence Threshold
    CONFIDENCE_THRESHOLD: float = 0.6
    MIN_SKILLS_LENGTH: int = 30
    MIN_EXPERIENCE_LENGTH: int = 100
    MIN_EDUCATION_LENGTH: int = 20
    
    # GitHub Features
    TOP_REPOS_COUNT: int = 3
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_MAX_BACKUP_COUNT: int = 7
    
    # API Response Configuration
    RESPONSE_TIMEOUT_SECONDS: int = 30
    MAX_RESUME_FILE_SIZE_MB: int = 10
    
    # Security Configuration
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: list = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = "INFO"


class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = True
    MONGO_URL = "mongodb://localhost:27017/"
    DATABASE_NAME = "skill_match_AI_test"
    LOG_LEVEL = "DEBUG"


def get_config() -> Config:
    """
    Get the appropriate configuration based on environment.
    
    Returns:
        Config: Configuration object for the current environment
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)()
