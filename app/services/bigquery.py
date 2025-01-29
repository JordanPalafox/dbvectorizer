import json
from datetime import datetime
from typing import List, Dict, Any
import logging
from google.cloud import bigquery
from google.oauth2 import service_account
from app.core.config import settings
from app.models.bigquery import ColumnMetadata, TableMetadata

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BigQueryService:
    def __init__(self):
        logger.info("Initializing BigQuery service...")
        credentials_info = settings.GCP_SERVICE_ACCOUNT_INFO
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        
        # Initialize with the project from service account
        self.project_id = settings.GCP_PROJECT_ID
        logger.info(f"Using service account project: {self.project_id}")
        
        self.client = bigquery.Client(
            credentials=credentials,
            project=self.project_id
        )

    async def extract_metadata(self, project_id: str = None) -> List[TableMetadata]:
        """Extract metadata from all datasets and tables in the project."""
        # Use provided project_id or fall back to service account project
        target_project = project_id or self.project_id
        logger.info(f"Extracting metadata from project: {target_project}")
        
        tables_metadata = []
        try:
            # List all datasets
            datasets = list(self.client.list_datasets(project=target_project))
            logger.info(f"Found {len(datasets)} datasets")
            
            for dataset in datasets:
                dataset_ref = self.client.dataset(dataset.dataset_id, project=target_project)
                logger.info(f"Processing dataset: {dataset.dataset_id}")
                
                # List all tables in dataset
                tables = list(self.client.list_tables(dataset_ref))
                logger.info(f"Found {len(tables)} tables in dataset {dataset.dataset_id}")
                
                for table in tables:
                    # Get full table details
                    table_ref = dataset_ref.table(table.table_id)
                    table_details = self.client.get_table(table_ref)
                    logger.info(f"Processing table: {table.table_id}")
                    
                    columns = []
                    for field in table_details.schema:
                        column = ColumnMetadata(
                            name=field.name,
                            data_type=field.field_type,
                            description=field.description,
                            table_name=table.table_id,
                            dataset_name=dataset.dataset_id,
                            project_id=target_project,
                            is_nullable=field.is_nullable,
                            mode=field.mode
                        )
                        columns.append(column)
                    
                    table_metadata = TableMetadata(
                        name=table.table_id,
                        dataset_name=dataset.dataset_id,
                        project_id=target_project,
                        description=table_details.description,
                        columns=columns,
                        created_time=table_details.created,
                        modified_time=table_details.modified
                    )
                    tables_metadata.append(table_metadata)
                    
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            raise Exception(f"Error extracting metadata: {str(e)}")
            
        return tables_metadata

    def get_all_columns(self, tables_metadata: List[TableMetadata]) -> List[ColumnMetadata]:
        """Extract all columns from tables metadata."""
        columns = []
        for table in tables_metadata:
            columns.extend(table.columns)
        return columns 