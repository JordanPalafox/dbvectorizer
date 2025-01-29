# DBVectorizer - BigQuery Metadata Vectorization Service

A REST API service that vectorizes BigQuery metadata using OpenAI embeddings and ChromaDB for efficient semantic search capabilities.

## Overview

DBVectorizer automatically extracts metadata from BigQuery tables, columns, and datasets, vectorizes this information using OpenAI's text-embedding-3-large model, and stores it in a local ChromaDB vector database. This enables semantic search capabilities across your data warehouse metadata.

## Tech Stack

- Python 3.9+
- FastAPI - REST API framework
- ChromaDB - Vector database
- OpenAI API - For embeddings (text-embedding-3-large) and chat completions (gpt-4-0125-preview)
- Google BigQuery API - For metadata extraction
- Docker & Docker Compose - Containerization
- Nginx - Reverse proxy
- Pydantic - Data validation and settings management

## Current Project Status

### Completed
- ✅ Basic project structure
- ✅ Environment configuration
- ✅ FastAPI application setup
- ✅ Docker configuration
- ✅ Nginx reverse proxy
- ✅ Health check endpoint
- ✅ Basic error handling

### Next Implementation Steps

1. BigQuery Metadata Models (`app/models/bigquery.py`)
```python
class ColumnMetadata(BaseModel):
    name: str
    data_type: str
    description: Optional[str]
    table_name: str
    dataset_name: str
    project_id: str
    is_nullable: bool
    mode: str  # NULLABLE, REQUIRED, REPEATED

class TableMetadata(BaseModel):
    name: str
    dataset_name: str
    project_id: str
    description: Optional[str]
    columns: List[ColumnMetadata]
    created_time: datetime
    modified_time: datetime
```

2. BigQuery Service (`app/services/bigquery.py`)
   - Initialize BigQuery client with service account
   - List all datasets in project
   - List all tables in each dataset
   - Extract column metadata for each table
   - Handle pagination and rate limits
   - Cache results to avoid repeated API calls

3. Vector Database Service (`app/services/vector_store.py`)
   - Initialize ChromaDB client
   - Create collection for metadata
   - Generate embeddings using OpenAI
   - Store column metadata with embeddings
   - Implement search functionality

4. Implementation Order:
   a. Create metadata extraction pipeline:
   ```python
   async def extract_metadata(project_id: str):
       # Initialize BigQuery client
       # List all datasets
       # For each dataset:
           # List all tables
           # For each table:
               # Get table schema and metadata
               # Extract column information
               # Create ColumnMetadata objects
       # Return complete metadata
   ```
   
   b. Create vectorization pipeline:
   ```python
   async def vectorize_metadata(metadata: List[ColumnMetadata]):
       # Initialize ChromaDB
       # For each column:
           # Generate embedding from column name
           # Store metadata and embedding
       # Return status
   ```

   c. Create search functionality:
   ```python
   async def search_metadata(query: str, top_k: int = 10):
       # Generate query embedding
       # Search ChromaDB
       # Return top_k results with metadata
   ```

## Prerequisites

- Docker and Docker Compose installed
- Google Cloud Service Account with BigQuery access
- OpenAI API key
- Python 3.9 or higher (for local development)

## Configuration

The service requires a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_CHAT_MODEL=gpt-4-0125-preview

# Google Cloud Configuration
GCP_PROJECT_ID=your_project_id
GCP_SERVICE_ACCOUNT={"type": "service_account", ...}  # Full JSON string of service account key

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./data/chromadb
CHROMA_COLLECTION_NAME=bigquery_metadata

# API Configuration
API_VERSION=v1
API_PREFIX=/api/${API_VERSION}
DEBUG=false

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## API Endpoints

### Currently Implemented
- `GET /api/v1/health` - Health check endpoint

### To Be Implemented
- `POST /api/v1/extract` - Trigger metadata extraction from BigQuery
  ```json
  {
    "project_id": "your-project-id",
    "force_refresh": false
  }
  ```
- `GET /api/v1/status` - Check extraction status
- `POST /api/v1/search` - Search for similar columns
  ```json
  {
    "query": "customer email address",
    "top_k": 10
  }
  ```

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dbvectorizer.git
cd dbvectorizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

## Docker Deployment

1. Build and start the containers:
```bash
docker-compose up --build
```

2. Access the API at `http://localhost/api/v1`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 