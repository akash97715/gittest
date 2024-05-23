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
    
    def process_batch(self, texts):
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

    def update_dataframe(self, batch_indices, embeddings_list, error_message=None):
        for idx, embeddings in zip(batch_indices, embeddings_list):
            if error_message:
                self.df.loc[idx, 'embedding'] = error_message
            else:
                self.df.loc[idx, 'embedding'] = json.dumps(embeddings)

    def process_parquet(self):
        batch_size = 16
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for start in range(0, len(self.df), batch_size):
                end = min(start + batch_size, len(self.df))
                batch_indices = self.df.index[start:end]
                texts = self.df.loc[batch_indices, 'text'].tolist()
                futures.append(executor.submit(self.process_batch, texts))
            
            for future in as_completed(futures):
                try:
                    embeddings, total_token = future.result()
                    if embeddings is None:
                        self.update_dataframe(batch_indices, [None]*batch_size, total_token)
                    else:
                        self.update_dataframe(batch_indices, embeddings)
                except Exception as e:
                    logger.error(f"Error in future: {str(e)}")
        
        self.df.to_parquet(self.parquet_path, index=False)

# Example usage:
if __name__ == "__main__":
    loader = EmbeddingLoader(
        parquet_path="path/to/your.parquet",
        engine="your_engine",
        client_id="your_client_id",
        x_vsl_client_id="your_x_vsl_client_id",
        bearer_token="your_bearer_token"
    )
    loader.process_parquet()
