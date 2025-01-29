from datetime import datetime
from typing import List, Optional, Dict

class ColumnMetadata:
    def __init__(
        self,
        name: str,
        data_type: str,
        table_name: str,
        dataset_name: str,
        project_id: str,
        is_nullable: bool,
        mode: str,
        description: Optional[str] = None
    ):
        self.name = name
        self.data_type = data_type
        self.description = description
        self.table_name = table_name
        self.dataset_name = dataset_name
        self.project_id = project_id
        self.is_nullable = is_nullable
        self.mode = mode

    def get_embedding_text(self) -> str:
        """Generate text to be used for embedding."""
        parts = [
            f"Column Name: {self.name}",
            f"Data Type: {self.data_type}",
            f"Table: {self.dataset_name}.{self.table_name}",
        ]
        if self.description:
            parts.append(f"Description: {self.description}")
        return " | ".join(parts)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "data_type": self.data_type,
            "description": self.description,
            "table_name": self.table_name,
            "dataset_name": self.dataset_name,
            "project_id": self.project_id,
            "is_nullable": self.is_nullable,
            "mode": self.mode
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ColumnMetadata':
        """Create from dictionary."""
        return cls(**data)

class TableMetadata:
    def __init__(
        self,
        name: str,
        dataset_name: str,
        project_id: str,
        columns: List[ColumnMetadata],
        created_time: datetime,
        modified_time: datetime,
        description: Optional[str] = None
    ):
        self.name = name
        self.dataset_name = dataset_name
        self.project_id = project_id
        self.description = description
        self.columns = columns
        self.created_time = created_time
        self.modified_time = modified_time

class ExtractRequest:
    def __init__(self, project_id: str, force_refresh: bool = False):
        self.project_id = project_id
        self.force_refresh = force_refresh

class SearchRequest:
    def __init__(self, query: str, top_k: int = 10):
        if not isinstance(top_k, int) or not 1 <= top_k <= 100:
            raise ValueError("top_k must be an integer between 1 and 100")
        self.query = query
        self.top_k = top_k

class SearchResponse:
    def __init__(self, results: List[ColumnMetadata], query: str):
        self.results = results
        self.total = len(results)
        self.query = query 