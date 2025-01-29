import logging
from typing import List, Optional
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

from app.core.config import settings
from app.models.postgres import ColumnMetadata, TableMetadata

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgresService:
    def __init__(self):
        logger.info("Initializing PostgreSQL service...")
        self.connection_params = {
            "host": settings.POSTGRES_HOST,
            "port": settings.POSTGRES_PORT,
            "database": settings.POSTGRES_DB,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD
        }

    def _get_connection(self):
        return psycopg2.connect(**self.connection_params)

    async def extract_metadata(self, schema: str = "public") -> List[TableMetadata]:
        """Extract metadata from all tables in the specified schema."""
        logger.info(f"Extracting metadata from schema: {schema}")
        
        tables_metadata = []
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    # Get all tables in the schema
                    cur.execute("""
                        SELECT 
                            table_name,
                            obj_description((quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass, 'pg_class') as table_description,
                            pg_stat_all_tables.reltuples::bigint as row_count,
                            pg_class.relcreated as created_time,
                            pg_stat_all_tables.last_vacuum as modified_time
                        FROM information_schema.tables
                        JOIN pg_stat_all_tables ON tables.table_name = pg_stat_all_tables.relname
                        JOIN pg_class ON pg_class.relname = tables.table_name
                        WHERE table_schema = %s
                        AND table_type = 'BASE TABLE'
                    """, (schema,))
                    
                    tables = cur.fetchall()
                    logger.info(f"Found {len(tables)} tables in schema {schema}")

                    for table in tables:
                        # Get column information for each table
                        cur.execute("""
                            SELECT 
                                column_name,
                                data_type,
                                is_nullable,
                                col_description((table_schema || '.' || table_name)::regclass, ordinal_position) as column_description
                            FROM information_schema.columns
                            WHERE table_schema = %s
                            AND table_name = %s
                            ORDER BY ordinal_position
                        """, (schema, table['table_name']))
                        
                        columns_data = cur.fetchall()
                        columns = []
                        
                        for col in columns_data:
                            column = ColumnMetadata(
                                name=col['column_name'],
                                data_type=col['data_type'],
                                description=col['column_description'],
                                table_name=table['table_name'],
                                schema_name=schema,
                                is_nullable=col['is_nullable'] == 'YES',
                                mode='NULLABLE' if col['is_nullable'] == 'YES' else 'REQUIRED'
                            )
                            columns.append(column)
                        
                        table_metadata = TableMetadata(
                            name=table['table_name'],
                            schema_name=schema,
                            description=table['table_description'],
                            columns=columns,
                            created_time=table['created_time'] if table['created_time'] else datetime.now(),
                            modified_time=table['modified_time'] if table['modified_time'] else datetime.now(),
                            row_count=table['row_count']
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