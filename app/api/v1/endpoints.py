from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import Dict, Any
import logging
from app.models.bigquery import ExtractRequest, SearchRequest, SearchResponse, ColumnMetadata
from app.services.bigquery import BigQueryService
from app.services.vector_store import VectorStoreService
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
bigquery_service = BigQueryService()
vector_store = VectorStoreService()

# Store extraction status
extraction_status: Dict[str, Any] = {
    "is_running": False,
    "last_error": None,
    "last_success": None
}

async def extract_and_vectorize(project_id: str, force_refresh: bool = False):
    """Background task to extract and vectorize metadata."""
    global extraction_status
    logger.info(f"Starting metadata extraction for project: {project_id}")
    
    try:
        extraction_status["is_running"] = True
        extraction_status["last_error"] = None
        
        # Extract metadata from BigQuery
        logger.info("Extracting metadata from BigQuery...")
        tables_metadata = await bigquery_service.extract_metadata(project_id)
        columns = bigquery_service.get_all_columns(tables_metadata)
        logger.info(f"Found {len(tables_metadata)} tables with {len(columns)} total columns")
        
        # Reset collection if force refresh
        if force_refresh:
            logger.info("Force refresh requested, resetting collection...")
            await vector_store.reset_collection()
        
        # Store in vector database
        logger.info("Storing metadata in vector database...")
        await vector_store.store_metadata(columns)
        
        extraction_status["last_success"] = {
            "project_id": project_id,
            "tables_count": len(tables_metadata),
            "columns_count": len(columns)
        }
        logger.info("Metadata extraction and vectorization completed successfully")
        
    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")
        extraction_status["last_error"] = str(e)
        raise
    finally:
        extraction_status["is_running"] = False

@router.post("/extract")
async def extract_metadata(
    background_tasks: BackgroundTasks,
    project_id: str = Query(None, description="The GCP project ID to extract metadata from (defaults to service account project)"),
    force_refresh: bool = Query(False, description="Whether to reset the collection before extraction")
):
    """Trigger metadata extraction from BigQuery."""
    # Use project ID from service account if none provided
    actual_project_id = project_id or settings.GCP_PROJECT_ID
    logger.info(f"Received extraction request for project: {actual_project_id}")
    
    if extraction_status["is_running"]:
        logger.warning("Extraction already in progress")
        raise HTTPException(
            status_code=409,
            detail="Extraction already in progress"
        )
    
    request = ExtractRequest(project_id=actual_project_id, force_refresh=force_refresh)
    background_tasks.add_task(
        extract_and_vectorize,
        request.project_id,
        request.force_refresh
    )
    
    logger.info("Extraction task queued")
    return {
        "message": "Extraction started",
        "status": "running",
        "project_id": actual_project_id
    }

@router.get("/status")
async def get_status():
    """Get the current status of metadata extraction."""
    logger.info("Getting extraction status")
    return extraction_status

@router.get("/embeddings/status")
async def get_embeddings_status():
    """Get the current status of embeddings in ChromaDB."""
    logger.info("Getting embeddings status")
    stats = vector_store.get_collection_stats()
    return {
        "embeddings_status": stats,
        "extraction_status": extraction_status["last_success"]
    }

@router.post("/search")
async def search_metadata(
    query: str = Query(..., description="The search query"),
    top_k: int = Query(10, ge=1, le=100, description="Number of results to return")
):
    """Search for similar columns."""
    logger.info(f"Received search request: query='{query}', top_k={top_k}")
    
    if extraction_status["last_success"] is None:
        logger.warning("Search attempted before extraction")
        raise HTTPException(
            status_code=400,
            detail="No metadata has been extracted yet. Please run extraction first."
        )
    
    try:
        request = SearchRequest(query=query, top_k=top_k)
    except ValueError as e:
        logger.error(f"Invalid search parameters: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    logger.info("Performing search...")
    results = await vector_store.search_metadata(
        query=request.query,
        top_k=request.top_k
    )
    
    response = SearchResponse(results=results, query=request.query)
    logger.info(f"Search completed, found {len(results)} results")
    return {
        "results": [col.to_dict() for col in response.results],
        "total": response.total,
        "query": response.query
    } 