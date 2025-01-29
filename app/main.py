from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import endpoints

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
    
    # Add health check endpoint
    @application.get(f"{settings.API_PREFIX}/health")
    async def health_check():
        return {"status": "healthy"}
    
    # Include API router
    application.include_router(
        endpoints.router,
        prefix=settings.API_PREFIX
    )
    
    return application

app = create_application() 