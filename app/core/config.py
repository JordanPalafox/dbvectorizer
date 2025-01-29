from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import json

class Settings(BaseSettings):
    # API Configuration
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    DEBUG: bool = False
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    OPENAI_CHAT_MODEL: str = "gpt-4-0125-preview"
    
    # Google Cloud Configuration
    GCP_PROJECT_ID: str
    GCP_SERVICE_ACCOUNT: str
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./data/chromadb"
    CHROMA_COLLECTION_NAME: str = "bigquery_metadata"
    
    @validator("GCP_SERVICE_ACCOUNT")
    def validate_service_account(cls, v: str) -> str:
        try:
            json.loads(v)
            return v
        except json.JSONDecodeError:
            raise ValueError("GCP_SERVICE_ACCOUNT must be a valid JSON string")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 