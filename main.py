import pandas as pd
import requests
import json
from typing import List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Placeholder for your constants and exceptions
IAS_EMBEDDINGS_URL = "https://api.example.com/embeddings"

class GenericException(Exception):
    pass

def get_auth_token(bearer_token: str) -> str:
    # Placeholder for your token generation logic
    return "your_generated_token"

def ias_openai_embeddings(
    raw_text: List[str],
    engine: str,
    client_id: str = None,
    x_vsl_client_id: str = None,
    bearer_token: str = None,
):
    try:
        url = IAS_EMBEDDINGS_URL
        payload = {"input": raw_text, "engine": engine}
        token = get_auth_token(bearer_token)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

        if x_vsl_client_id is not None:
            headers["x-vsl-client_id"] = x_vsl_client_id
        elif client_id is not None:
            headers["x-vsl-client_id"] = client_id

        logger.info("Triggering embedding endpoint")
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(
                f"Error calling OpenAI embedding API: {response.status_code}, {response.json()}"
            )
            raise GenericException(
                f"Error calling OpenAI embedding API: {response.status_code}, {response.json()}",
                status_code=response.status_code,
            )

        embeddings = json.loads(response.json()["result"])
        temp = response.json()
        total_token = temp['totalTokens']        
        logger.info("Received response from embedding endpoint")

        return embeddings, total_token
    except Exception as e:
        logger.error("Got the Exception: %s", str(e))
        raise GenericException(e)

class EmbeddingLoader:
    def __init__(self, parquet_path, engine, client_id, x_vsl_client_id=None, bearer_token=None, max_retries=3):
        self.parquet_path = parquet_path
        self.engine = engine
        self.client_id = client_id
        self.x_vsl_client_id = x_vsl_client_id
        self.bearer_token = bearer_token
        self.max_retries = max_retries
        self.df = pd.read_parquet(parquet_path)
    
    def process_row(self, texts):
        for attempt in range(self.max_retries):
            try:
                embeddings, total_token = ias_openai_embeddings(
                    texts, self.engine, self.client_id, self.x_vsl_client_id, self.bearer_token
                )
                return embeddings, total_token
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed with error: {str(e)}")
                if attempt == self.max_retries - 1:
                    return None, str(e)
        return None, "Maximum retries exceeded"

    def update_dataframe(self, idx, embeddings_list, error_message=None):
        if error_message:
            self.df.at[idx, 'embedding'] = error_message
            self.df.at[idx, 'status'] = 'failed'
        else:
            self.df.at[idx, 'embedding'] = json.dumps(embeddings_list)
            self.df.at[idx, 'status'] = 'success'

    def process_parquet(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for idx in self.df.index:
                texts = self.df.at[idx, 'chunk']
                futures.append((idx, executor.submit(self.process_row, texts)))
            
            for idx, future in futures:
                try:
                    embeddings, total_token = future.result()
                    if embeddings is None:
                        self.update_dataframe(idx, None, total_token)
                    else:
                        self.update_dataframe(idx, embeddings)
                except Exception as e:
                    logger.error(f"Error in future for index {idx}: {str(e)}")
        
        self.df.to_parquet(self.parquet_path, index=False)
        print(f"Updated Parquet file saved at {self.parquet_path}")

# Example usage:
if __name__ == "__main__":
    # First, create the initial Parquet file with chunks and metadata
    chunks = [
        ["chunk1_item1", "chunk1_item2", "chunk1_item3", "chunk1_item4", "chunk1_item5",
         "chunk1_item6", "chunk1_item7", "chunk1_item8", "chunk1_item9", "chunk1_item10",
         "chunk1_item11", "chunk1_item12", "chunk1_item13", "chunk1_item14", "chunk1_item15"],
        ["chunk2_item1", "chunk2_item2", "chunk2_item3", "chunk2_item4", "chunk2_item5",
         "chunk2_item6", "chunk2_item7", "chunk2_item8", "chunk2_item9", "chunk2_item10",
         "chunk2_item11", "chunk2_item12", "chunk2_item13", "chunk2_item14", "chunk2_item15"]
    ]
    metadata = [
        ["metadata1_item1", "metadata1_item2", "metadata1_item3", "metadata1_item4", "metadata1_item5",
         "metadata1_item6", "metadata1_item7", "metadata1_item8", "metadata1_item9", "metadata1_item10",
         "metadata1_item11", "metadata1_item12", "metadata1_item13", "metadata1_item14", "metadata1_item15"],
        ["metadata2_item1", "metadata2_item2", "metadata2_item3", "metadata2_item4", "metadata2_item5",
         "metadata2_item6", "metadata2_item7", "metadata2_item8", "metadata2_item9", "metadata2_item10",
         "metadata2_item11", "metadata2_item12", "metadata2_item13", "metadata2_item14", "metadata2_item15"]
    ]
    initial_parquet_path = "path/to/your_initial.parquet"

    file_loader = FileLoader(chunks, metadata, initial_parquet_path)
    file_loader.create_parquet()

    # Then, process the Parquet file to generate embeddings
    embedding_loader = EmbeddingLoader(
        parquet_path=initial_parquet_path,
        engine="your_engine",
        client_id="your_client_id",
        x_vsl_client_id="your_x_vsl_client_id",
        bearer_token="your_bearer_token"
    )
    embedding_loader.process_parquet()
