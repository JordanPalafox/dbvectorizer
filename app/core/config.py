import json
import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

def load_service_account() -> dict:
    """Load service account from environment variable."""
    try:
        sa_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        if not sa_json:
            raise ValueError("GCP_SERVICE_ACCOUNT_JSON environment variable not set")
        
        sa_dict = json.loads(sa_json)
            
        # Validate required fields
        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        missing_fields = [field for field in required_fields if field not in sa_dict]
        
        if missing_fields:
            raise ValueError(f"Service account JSON is missing required fields: {', '.join(missing_fields)}")
        
        if sa_dict["type"] != "service_account":
            raise ValueError("JSON must be a service account key (type should be 'service_account')")
            
        return sa_dict
    except json.JSONDecodeError as e:
        print(f"Error parsing GCP_SERVICE_ACCOUNT_JSON: {str(e)}")
        raise
    except Exception as e:
        print(f"Error loading service account from environment: {str(e)}")
        raise

class Settings:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # API Configuration
        self.API_VERSION = "v1"
        self.API_PREFIX = f"/api/{self.API_VERSION}"
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        
        # Server Configuration
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        
        # OpenAI Configuration
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in environment")
            
        self.OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        self.OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4-0125-preview")
        
        # ChromaDB Configuration
        self.CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chromadb")
        self.CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "bigquery_metadata")
        
        # Google Cloud Configuration - These will be set after initialization
        self.GCP_PROJECT_ID: Optional[str] = None
        self.GCP_SERVICE_ACCOUNT_INFO: Optional[Dict] = None

# Initialize settings with better error handling
try:
    # First create settings with environment variables
    settings = Settings()
    
    # Then load and set service account info
    service_account_info = load_service_account()
    settings.GCP_SERVICE_ACCOUNT_INFO = service_account_info
    settings.GCP_PROJECT_ID = service_account_info["project_id"]
    
except Exception as e:
    print("Error loading settings:")
    print(f"1. Make sure .env file exists at: {os.path.abspath('.env')}")
    print(f"2. Make sure gcp_sa.json exists at: {os.path.abspath('gcp_sa.json')}")
    print("3. Check that all required environment variables are set")
    print(f"\nError details: {str(e)}")
    raise 