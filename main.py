import pandas as pd
from opensearchpy.helpers import BulkIndexError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the parquet file
file_path = '/mnt/data/your_parquet_file.parquet'  # Update this to the actual file path if it's different
df = pd.read_parquet(file_path)

# Prepare the parameters for the add_embeddings function
text_embeddings = list(zip(df['chunk'].tolist(), df['embedding'].tolist()))
metadatas = df['metadata'].tolist()

# Function to add embeddings with retry logic
def process_embeddings(add_embeddings_func, text_embeddings, metadatas, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            add_embeddings_func(text_embeddings=text_embeddings, metadatas=metadatas)
            logger.info("Successfully ingested all embeddings")
            break
        except BulkIndexError as e:
            retries += 1
            logger.error(f"BulkIndexError: {e.errors}")
            if retries >= max_retries:
                logger.error(f"Failed to index after {max_retries} retries")
            else:
                logger.info(f"Retrying, attempt {retries + 1}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            break

# Assuming add_embeddings is a method of an instantiated class, use `instance.add_embeddings`
# Replace `instance` with the actual instance of the class
process_embeddings(instance.add_embeddings, text_embeddings, metadatas)
