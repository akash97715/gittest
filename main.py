import pandas as pd
import boto3
import uuid
from typing import List
import json
from fastapi import HTTPException
import httpx
import requests
from concurrent.futures import ThreadPoolExecutor
from app.utils.custom_loguru import logger
from external_api import ias_openai_embeddings  # Assuming this is where the function is

class ParquetEmbeddingProcessor:
    def __init__(
        self,
        chunks: List[str] = None,
        metadata: List[str] = None,
        s3_bucket: str = None,
        s3_prefix: str = None,
        parquet_path: str = None,
        engine: str = None,
        client_id: str = None,
        x_vsl_client_id: str = None,
        bearer_token: str = None,
        max_retries: int = 3
    ):
        self.chunks = chunks
        self.metadata = metadata
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.parquet_path = parquet_path
        self.engine = engine
        self.client_id = client_id
        self.x_vsl_client_id = x_vsl_client_id
        self.bearer_token = bearer_token if bearer_token else self.federate_auth()
        self.max_retries = max_retries
        self.df = self.load_parquet(parquet_path) if parquet_path else None

    def create_parquet(self) -> str:
        # Create a DataFrame with the initial data
        data = {
            "chunk": self.chunks,
            "metadata": self.metadata,
            "embedding": [None] * len(self.chunks),
            "embedding_status": [""] * len(self.chunks),
            "os_ingestion_status": [""] * len(self.chunks),
            "embedding_error_count": [""] * len(self.chunks),
            "embedding_error_message": [None] * len(self.chunks),
        }
        self.df = pd.DataFrame(data)

        # Generate a unique filename
        parquet_filename = f"{uuid.uuid4()}.parquet"
        local_parquet_path = f"ingest_pipeline/{parquet_filename}"

        # Save the DataFrame to a Parquet file locally
        self.df.to_parquet(local_parquet_path, index=False)
        print(f"Parquet file created locally at {local_parquet_path}")

        # Upload the Parquet file to S3
        s3_client = boto3.client("s3")
        s3_key = f"{self.s3_prefix}/{parquet_filename}"
        s3_client.upload_file(local_parquet_path, self.s3_bucket, s3_key)
        print(f"Parquet file uploaded to s3://{self.s3_bucket}/{s3_key}")

        # Return the S3 URI
        s3_uri = f"s3://{self.s3_bucket}/{s3_key}"
        return s3_uri

    @staticmethod
    def load_parquet(s3_uri: str) -> pd.DataFrame:
        # Parse the S3 URI
        s3_path = s3_uri.replace("s3://", "")
        bucket, key = s3_path.split("/", 1)

        # Download the Parquet file from S3
        s3_client = boto3.client("s3")
        local_parquet_path = f"ingest_pipeline/{key.split('/')[-1]}"
        s3_client.download_file(bucket, key, local_parquet_path)
        print(f"Parquet file downloaded locally at {local_parquet_path}")

        # Load the Parquet file into a DataFrame
        df = pd.read_parquet(local_parquet_path)
        return df

    @staticmethod
    def save_parquet(df: pd.DataFrame, parquet_path: str):
        df.to_parquet(parquet_path, index=False)
        print(f"Parquet file saved at {parquet_path}")

    def federate_auth(self):
        # Implement federated authentication here if needed
        return "your_bearer_token"

    def process_row(self, texts):
        for attempt in range(self.max_retries):
            try:
                embeddings = ias_openai_embeddings(token=self.bearer_token, raw_text=texts, engine=self.engine)
                return embeddings, None
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed with error: {str(e)}")
                if attempt == self.max_retries - 1:
                    return None, str(e)
        return None, "Maximum retries exceeded"

    def update_dataframe(self, idx, embeddings_list, error_message=None):
        if error_message:
            self.df.at[idx, 'embedding'] = error_message
            self.df.at[idx, 'embedding_status'] = 'failed'
        else:
            self.df.at[idx, 'embedding'] = json.dumps(embeddings_list)
            self.df.at[idx, 'embedding_status'] = 'success'

    def process_parquet(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for idx in self.df.index:
                texts = self.df.at[idx, 'chunk']
                futures.append((idx, executor.submit(self.process_row, texts)))
            for idx, future in futures:
                try:
                    embeddings, error_message = future.result()
                    if embeddings is None:
                        self.update_dataframe(idx, None, error_message)
                    else:
                        self.update_dataframe(idx, embeddings)
                except Exception as e:
                    logger.error(f"Error in future for index {idx}: {str(e)}")
        self.save_parquet(self.df, self.parquet_path)
        print(f"Updated Parquet file saved at {self.parquet_path}")
