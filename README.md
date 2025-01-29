# DBVectorizer - BigQuery Metadata Vectorization Service

A REST API service that vectorizes BigQuery metadata using OpenAI embeddings and ChromaDB for efficient semantic search capabilities.

## Overview

DBVectorizer automatically extracts metadata from BigQuery tables, columns, and datasets, vectorizes this information using OpenAI's text-embedding-3-large model, and stores it in a local ChromaDB vector database. This enables semantic search capabilities across your data warehouse metadata.

## Tech Stack

- Python 3.9+
- FastAPI - REST API framework
- ChromaDB - Vector database
- OpenAI API - Para embeddings (text-embedding-3-large) y chat completions (gpt-4-0125-preview)
- Google BigQuery API - Para extracción de metadatos
- Docker & Docker Compose - Containerización
- Nginx - Reverse proxy
- Pydantic - Validación de datos y gestión de configuraciones
- Pytest - Testing framework
- Tenacity - Manejo de reintentos y resiliencia
- Httpx - Cliente HTTP asíncrono

## Dependencias Principales

```txt
fastapi
uvicorn
python-dotenv
chromadb
openai
google-cloud-bigquery
python-multipart
httpx
pytest
pytest-asyncio
tenacity
numpy
```

## Current Project Status

### Completado
- ✅ Estructura básica del proyecto
- ✅ Configuración del entorno
- ✅ Configuración de FastAPI
- ✅ Configuración de Docker
- ✅ Nginx reverse proxy
- ✅ Endpoint de health check
- ✅ Manejo básico de errores
- ✅ Modelos de metadatos de BigQuery
- ✅ Servicio de BigQuery para extracción de metadatos
- ✅ Servicio de base de datos vectorial con ChromaDB
- ✅ Pipeline de extracción de metadatos
- ✅ Pipeline de vectorización
- ✅ Funcionalidad de búsqueda
- ✅ API REST completa con documentación

### Próximas Mejoras
1. Optimización de rendimiento
   - Implementar caché para resultados frecuentes
   - Mejorar la paginación de resultados
   - Optimizar el proceso de extracción para grandes conjuntos de datos

2. Mejoras de Funcionalidad
   - Añadir más métricas y estadísticas
   - Implementar búsqueda avanzada con filtros
   - Añadir soporte para múltiples proyectos
   - Implementar sistema de actualización incremental

## Prerequisites

- Docker and Docker Compose installed
- Google Cloud Service Account with BigQuery access
- OpenAI API key
- Python 3.9 or higher (for local development)

## Configuration

El servicio requiere un archivo `.env` con las siguientes variables:

```env
# Configuración de OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_CHAT_MODEL=gpt-4-0125-preview

# Configuración de Google Cloud
GCP_PROJECT_ID=your_project_id
GCP_SERVICE_ACCOUNT={"type": "service_account", ...}  # JSON completo de la cuenta de servicio

# Configuración de ChromaDB
CHROMA_PERSIST_DIRECTORY=./data/chromadb
CHROMA_COLLECTION_NAME=bigquery_metadata

# Configuración de la API
API_VERSION=v1
API_PREFIX=/api/${API_VERSION}
DEBUG=false

# Configuración del Servidor
HOST=0.0.0.0
PORT=8000
```

## API Endpoints

### Endpoints Implementados
- `GET /api/v1/health` - Health check endpoint
- `POST /api/v1/extract` - Inicia la extracción de metadatos de BigQuery
  ```json
  {
    "project_id": "your-project-id",  // Opcional, usa el proyecto por defecto si no se especifica
    "force_refresh": false  // Opcional, reinicia la colección si es true
  }
  ```
- `GET /api/v1/status` - Verifica el estado de la extracción de metadatos
- `GET /api/v1/embeddings/status` - Obtiene estadísticas de los embeddings en ChromaDB
- `POST /api/v1/search` - Busca columnas similares
  ```json
  {
    "query": "customer email address",
    "top_k": 10  // Opcional, por defecto 10, máximo 100
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

## Estructura del Proyecto

```
dbvectorizer/
├── app/
│   ├── models/
│   ├── services/
│   ├── api/
│   └── core/
├── data/
│   └── chromadb/
├── nginx/
├── tests/
├── .env
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
``` 