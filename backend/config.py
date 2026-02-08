"""
Configuration management for the Text-to-SQL Chatbot application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration class."""

    # Application Settings
    APP_NAME = os.getenv("APP_NAME", "Text-to-SQL Chatbot")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    
    # Server Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    
    # Database Settings
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    
    # SQLite Settings
    SQLITE_PATH = str(BASE_DIR / "data" / "database.db")
    
    # MySQL Settings (for future use)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "text_to_sql_db")
    
    @property
    def DATABASE_URI(self):
        if self.DB_TYPE == "sqlite":
            os.makedirs(os.path.dirname(self.SQLITE_PATH), exist_ok=True)
            return f"sqlite:///{self.SQLITE_PATH}"
        else:
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # RAG Settings
    CHROMA_PERSIST_DIR = str(BASE_DIR / "data" / "chroma")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_DIR = str(BASE_DIR / "logs")
    
    # File Upload Settings
    UPLOAD_FOLDER = str(BASE_DIR / "data" / "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"xlsx", "xls", "csv"}
    
    # Model backend switches
    USE_OPENAI_LLM = os.getenv("USE_OPENAI_LLM", "False").lower() == "true"
    USE_HF_LLM = os.getenv("USE_HF_LLM", "False").lower() == "true"
    USE_OLLAMA_LLM = os.getenv("USE_OLLAMA_LLM", "False").lower() == "true"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "INFO"


class TestingConfig(Config):
    TESTING = True
    DB_TYPE = "sqlite"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)()