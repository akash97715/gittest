import pandas as pd
from opensearchpy.helpers import BulkIndexError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the parquet file
file_path = '/mnt/data/Screenshot 2024-06-18 at 9.40.42 AM.png'  # Update this to the actual file path if it's different
df = pd.read_parquet(file_path)

# Define the batch size
batch_size = 500

# Prepare the parameters for the add_embeddings function
text_embeddings = list(zip(df['chunk'], df['embedding']))
metadatas = df['metadata'].tolist()

# Function to add embeddings in batches with retry logic
def process_in_batches(add_embeddings_func, text_embeddings, metadatas, batch_size, max_retries=3):
    for i in range(0, len(text_embeddings), batch_size):
        batch_text_embeddings = text_embeddings[i:i+batch_size]
        batch_metadatas = metadatas[i:i+batch_size]
        retries = 0
        while retries < max_retries:
            try:
                add_embeddings_func(text_embeddings=batch_text_embeddings, metadatas=batch_metadatas)
                logger.info(f"Successfully ingested batch starting at index {i}")
                break
            except BulkIndexError as e:
                retries += 1
                logger.error(f"BulkIndexError: {e.errors}")
                if retries >= max_retries:
                    logger.error(f"Failed to index batch starting at index {i} after {max_retries} retries")
                else:
                    logger.info(f"Retrying batch starting at index {i}, attempt {retries + 1}")
            except Exception as e:
                logger.exception(f"An unexpected error occurred: {e}")
                break

# Assuming add_embeddings is a method of an instantiated class, use `instance.add_embeddings`
# Replace `instance` with the actual instance of the class
process_in_batches(instance.add_embeddings, text_embeddings, metadatas, batch_size)
