import os
from typing import Optional, Dict
from pydantic import BaseModel

class IngestModel(BaseModel):
    textract_config: Optional[Dict] = {
        'ingest_table_content_details': 'plaintext', 
        'table_column_separator': '\t', 
        'table_row_separator': os.linesep
    }

# Example usage
def ingest(data: IngestModel):
    # Your function logic here
    print(data.textract_config)

# Example input data
example_data = {}
ingest_model_instance = IngestModel(**example_data)
ingest(ingest_model_instance)
