import os
from typing import Optional, Dict
from pydantic import BaseModel, Field

# Define default values
DEFAULT_TEXTRACT_CONFIG = {
    'ingest_table_content_details': 'plaintext',
    'table_column_separator': '\t',
    'table_row_separator': os.linesep
}

class IngestModel(BaseModel):
    textract_config: Optional[Dict[str, str]] = Field(default_factory=lambda: DEFAULT_TEXTRACT_CONFIG.copy())

def textractLinearizationConfig(ingest_table_content_details: str, table_column_separator: str, table_row_separator: str):
    # Function logic for textractLinearizationConfig
    print(f"ingest_table_content_details: {ingest_table_content_details}")
    print(f"table_column_separator: {table_column_separator}")
    print(f"table_row_separator: {table_row_separator}")

def ingest(data: IngestModel):
    # Extract values from textract_config with defaults
    config = DEFAULT_TEXTRACT_CONFIG.copy()
    config.update(data.textract_config or {})
    ingest_table_content_details = config.get('ingest_table_content_details')
    table_column_separator = config.get('table_column_separator')
    table_row_separator = config.get('table_row_separator')
    
    # Pass the values to textractLinearizationConfig
    textractLinearizationConfig(ingest_table_content_details, table_column_separator, table_row_separator)

# Example input data
example_data = {}  # Simulate missing user input
ingest_model_instance = IngestModel(**example_data)
ingest(ingest_model_instance)
