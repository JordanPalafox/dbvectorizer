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

# Google Cloud Configuration
GCP_PROJECT_ID=your_project_id
GCP_SERVICE_ACCOUNT={"type": "service_account", ... } # Full JSON string of service account key

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=/path/to/persist
```

## Development Steps

1. Initial Setup
   - Create project structure
   - Set up Docker configuration
   - Configure environment variables
   - Initialize FastAPI application

2. BigQuery Integration
   - Implement BigQuery client setup
   - Create metadata extraction service
   - Define metadata models using Pydantic
   - Implement metadata extraction pipeline

3. Vector Database Implementation
   - Set up ChromaDB integration
   - Implement embedding generation using OpenAI
   - Create vectorization pipeline
   - Define vector storage schema

4. API Development
   - Create REST endpoints
   - Implement metadata extraction endpoint
   - Create vector search endpoint
   - Add health check endpoints
   - Implement error handling

5. Docker Configuration
   - Create Dockerfile
   - Set up Docker Compose
   - Configure Nginx reverse proxy
   - Define volume mappings

6. Testing & Documentation
   - Write unit tests
   - Create integration tests
   - Generate API documentation
   - Write deployment guide

## API Endpoints

### Metadata Extraction
- `POST /api/v1/extract` - Trigger metadata extraction from BigQuery
- `GET /api/v1/status` - Check extraction status

### Vector Search
- `POST /api/v1/search` - Search for similar columns based on description
- Parameters:
  - `query`: Search query text
  - `top_k`: Number of results to return (default: 10)

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

2. Access the API at `http://localhost:8000`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 