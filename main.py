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
#IAS_EMBEDDINGS_URL = "https://api.example.com/embeddings"
 
class GenericException(Exception):
    pass
 
def get_auth_token(bearer_token: str) -> str:
    # Placeholder for your token generation logic
    return "your_generated_token"
 
def ias_openai_embeddings(token: str, raw_text, engine: str):
    try:
        url = IAS_EMBEDDINGS_URL
        payload = {"input": raw_text, "engine": engine}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        logger.info("Triggering embedding endpoint")
        response = requests.post(url, headers=headers, json=payload)
 
        if response.status_code != 200:
            logger.error(
                f"Error calling OpenAI embedding API: {response.status_code}, {response.json()}"
            )
            raise Exception(
                f"Error calling OpenAI embedding API: {response.status_code}, {response.json()}"
            )
 
        embeddings = json.loads(response.json()["result"])
        logger.info("Recevied response from embedding endpoint")
 
        return embeddings
    except Exception as e:
        logger.error("Got the Exception", str(e))
        # raising backoff exception
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
                embeddings, total_token = ias_openai_embeddings(token= self.bearer_token, raw_text=texts, engine=llm_embedding)
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
    #chunks = ["chunk1", "chunk2", "chunk3"]
    #metadata = ["metadata1", "metadata2", "metadata3"]
    initial_parquet_path = "chunk_embedding.parquet"
 
    #file_loader = FileLoader(chunks, metadata, initial_parquet_path)
    #file_loader.create_parquet()
 
    # Then, process the Parquet file to generate embeddings
    embedding_loader = EmbeddingLoader(
        parquet_path=initial_parquet_path,
        engine=llm_embedding,
        client_id=CLIENT_ID,
        x_vsl_client_id=CLIENT_ID,
        bearer_token=federate_auth()
    )
    embedding_loader.process_parquet()
