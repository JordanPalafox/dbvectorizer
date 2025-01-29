import chromadb
from chromadb.config import Settings
from openai import OpenAI
from typing import List, Dict, Any
import logging
from app.core.config import settings
from app.models.bigquery import ColumnMetadata as BigQueryColumnMetadata
from app.models.postgres import ColumnMetadata as PostgresColumnMetadata
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        logger.info("Initializing VectorStoreService...")
        
        # Initialize ChromaDB
        logger.info(f"Connecting to ChromaDB at {settings.CHROMA_PERSIST_DIRECTORY}")
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(allow_reset=True)
        )
        
        # Initialize OpenAI client
        logger.info("Initializing OpenAI client...")
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Get or create collection
        logger.info(f"Getting or creating collection: {settings.CHROMA_COLLECTION_NAME}")
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Log collection status
        count = self.collection.count()
        logger.info(f"Collection has {count} embeddings")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API."""
        logger.info(f"Generating embedding for text: {text[:100]}...")
        response = self.openai_client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text
        )
        logger.info("Embedding generated successfully")
        return response.data[0].embedding

    def _clean_metadata(self, metadata: Dict) -> Dict:
        """Clean metadata dictionary by removing None values and ensuring proper types."""
        cleaned = {}
        for key, value in metadata.items():
            # Skip None values
            if value is None:
                continue
            # Convert to appropriate type
            if isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            else:
                # Convert other types to string
                cleaned[key] = str(value)
        return cleaned

    def _generate_column_id(self, column: Any) -> str:
        """Generate a unique ID for a column based on its type."""
        if isinstance(column, BigQueryColumnMetadata):
            return f"bq.{column.project_id}.{column.dataset_name}.{column.table_name}.{column.name}"
        elif isinstance(column, PostgresColumnMetadata):
            return f"pg.{column.schema_name}.{column.table_name}.{column.name}"
        else:
            raise ValueError(f"Unsupported column type: {type(column)}")

    async def store_metadata(self, columns: List[Any]) -> None:
        """Store column metadata in ChromaDB with embeddings."""
        logger.info(f"Storing metadata for {len(columns)} columns...")
        
        successful_count = 0
        failed_count = 0
        
        for column in columns:
            try:
                # Prepare data for single column
                text = column.get_embedding_text()
                id = self._generate_column_id(column)
                
                # Clean metadata
                raw_metadata = column.to_dict()
                metadata = self._clean_metadata(raw_metadata)
                
                # Add source type to metadata
                metadata['source_type'] = 'bigquery' if isinstance(column, BigQueryColumnMetadata) else 'postgres'
                
                # Generate embedding with rate limiting
                logger.info(f"Generating embedding for column: {id}")
                embedding = self.generate_embedding(text)
                
                # Add single embedding to ChromaDB
                self.collection.add(
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[metadata],
                    ids=[id]
                )
                successful_count += 1
                logger.info(f"Successfully stored embedding {successful_count}/{len(columns)}")
                
                # Rate limiting delay
                time.sleep(0.3)
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to process column {column.name}: {str(e)}")
                continue
        
        logger.info(f"Embedding storage complete. Success: {successful_count}, Failed: {failed_count}")

    async def search_metadata(self, query: str, top_k: int = 10) -> List[Any]:
        """Search for similar columns using the query."""
        logger.info(f"Searching for: {query} (top_k={top_k})")
        
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)
        
        # Search in ChromaDB
        logger.info("Searching in ChromaDB...")
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "distances"]
        )
        
        # Convert results back to appropriate ColumnMetadata objects
        columns = []
        for metadata in results["metadatas"][0]:
            # Remove source_type from metadata before creating objects
            source_type = metadata.pop('source_type', 'postgres')  # default to postgres if not found
            
            # Remove any other fields that aren't part of the model
            cleaned_metadata = {
                k: v for k, v in metadata.items() 
                if k in ['name', 'data_type', 'description', 'table_name', 'schema_name', 
                        'is_nullable', 'mode', 'project_id', 'dataset_name']
            }
            
            if source_type == 'bigquery':
                columns.append(BigQueryColumnMetadata.from_dict(cleaned_metadata))
            else:
                columns.append(PostgresColumnMetadata.from_dict(cleaned_metadata))
        
        logger.info(f"Found {len(columns)} results")
        return columns

    async def reset_collection(self) -> None:
        """Reset the collection. Useful when force_refresh is True."""
        logger.info(f"Resetting collection: {settings.CHROMA_COLLECTION_NAME}")
        self.chroma_client.delete_collection(settings.CHROMA_COLLECTION_NAME)
        self.collection = self.chroma_client.create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Collection reset complete")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the current collection."""
        logger.info("Getting collection statistics...")
        try:
            count = self.collection.count()
            peek = self.collection.peek(limit=1) if count > 0 else None
            
            stats = {
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "total_embeddings": count,
                "has_data": count > 0,
                "sample_id": peek["ids"][0] if peek else None,
                "persist_directory": settings.CHROMA_PERSIST_DIRECTORY,
                "embedding_model": settings.OPENAI_EMBEDDING_MODEL
            }
            logger.info(f"Collection stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {
                "error": str(e),
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "has_data": False,
                "persist_directory": settings.CHROMA_PERSIST_DIRECTORY,
                "embedding_model": settings.OPENAI_EMBEDDING_MODEL
            } 