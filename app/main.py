from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def create_application() -> FastAPI:
    application = FastAPI(
        title="DBVectorizer",
        description="BigQuery Metadata Vectorization Service",
        version="1.0.0",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        debug=settings.DEBUG
    )
    
    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @application.get(f"{settings.API_PREFIX}/health")
    async def health_check():
        return {"status": "healthy"}
    
    return application

app = create_application() 