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
                    # Primero verificamos si el esquema existe
                    cur.execute("""
                        SELECT EXISTS(
                            SELECT 1 
                            FROM information_schema.schemata 
                            WHERE schema_name = %s
                        )
                    """, (schema,))
                    
                    schema_exists = cur.fetchone()[0]
                    if not schema_exists:
                        logger.warning(f"Schema {schema} does not exist")
                        return []

                    # Get all tables in the schema with their metadata
                    cur.execute("""
                        SELECT 
                            t.table_name,
                            pg_catalog.pg_get_userbyid(pgc.relowner) as table_owner,
                            pgc.reltuples::bigint as estimated_row_count,
                            GREATEST(
                                pg_stat_get_last_vacuum_time(pgc.oid),
                                pg_stat_get_last_autovacuum_time(pgc.oid),
                                pg_stat_get_last_analyze_time(pgc.oid),
                                pg_stat_get_last_autoanalyze_time(pgc.oid)
                            ) as last_modified
                        FROM information_schema.tables t
                        JOIN pg_catalog.pg_class pgc ON pgc.relname = t.table_name
                        JOIN pg_catalog.pg_namespace pgn ON pgn.oid = pgc.relnamespace 
                            AND pgn.nspname = t.table_schema
                        WHERE t.table_schema = %s
                        AND t.table_type = 'BASE TABLE'
                        AND has_table_privilege(pgc.oid, 'SELECT')
                    """, (schema,))
                    
                    tables = cur.fetchall()
                    logger.info(f"Found {len(tables)} accessible tables in schema {schema}")

                    for table in tables:
                        try:
                            # Get table description safely
                            cur.execute("""
                                SELECT description 
                                FROM pg_catalog.pg_description pd
                                JOIN pg_catalog.pg_class pc ON pd.objoid = pc.oid
                                JOIN pg_catalog.pg_namespace pn ON pc.relnamespace = pn.oid
                                WHERE pc.relname = %s
                                AND pn.nspname = %s
                                AND pd.objsubid = 0
                            """, (table['table_name'], schema))
                            description_row = cur.fetchone()
                            table_description = description_row['description'] if description_row else None

                            # Get column information for each table
                            cur.execute("""
                                WITH column_descriptions AS (
                                    SELECT 
                                        pd.objsubid as ordinal_position,
                                        pd.description
                                    FROM pg_catalog.pg_description pd
                                    JOIN pg_catalog.pg_class pc ON pd.objoid = pc.oid
                                    JOIN pg_catalog.pg_namespace pn ON pc.relnamespace = pn.oid
                                    WHERE pc.relname = %s
                                    AND pn.nspname = %s
                                    AND pd.objsubid > 0
                                )
                                SELECT 
                                    c.column_name,
                                    c.data_type,
                                    c.is_nullable,
                                    cd.description as column_description,
                                    c.ordinal_position
                                FROM information_schema.columns c
                                LEFT JOIN column_descriptions cd 
                                    ON cd.ordinal_position = c.ordinal_position::integer
                                WHERE c.table_schema = %s
                                AND c.table_name = %s
                                ORDER BY c.ordinal_position
                            """, (table['table_name'], schema, schema, table['table_name']))
                            
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
                                description=table_description,
                                columns=columns,
                                created_time=datetime.now(),  # PostgreSQL no almacena la fecha de creación por defecto
                                modified_time=table['last_modified'] if table['last_modified'] else datetime.now(),
                                row_count=table['estimated_row_count']
                            )
                            tables_metadata.append(table_metadata)
                            
                        except Exception as table_error:
                            logger.warning(f"Error processing table {table['table_name']}: {str(table_error)}")
                            continue
                    
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