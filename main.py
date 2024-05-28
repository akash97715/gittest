import pandas as pd
import boto3
import uuid
from typing import List

class ParquetHelper:
    def __init__(self, chunks: List[str] = None, metadata: List[str] = None, s3_bucket: str = None, s3_prefix: str = None):
        self.chunks = chunks
        self.metadata = metadata
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix

    def create_parquet(self) -> str:
        # Create a DataFrame with the initial data
        data = {
            'chunk': self.chunks,
            'metadata': self.metadata,
            'embedding': [None] * len(self.chunks),
            'status': [''] * len(self.chunks)
        }
        df = pd.DataFrame(data)

        # Generate a unique filename
        parquet_filename = f"{uuid.uuid4()}.parquet"
        local_parquet_path = f"/tmp/{parquet_filename}"

        # Save the DataFrame to a Parquet file locally
        df.to_parquet(local_parquet_path, index=False)
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
        bucket, key = s3_path.split('/', 1)

        # Download the Parquet file from S3
        s3_client = boto3.client('s3')
        local_parquet_path = f"/tmp/{key.split('/')[-1]}"
        s3_client.download_file(bucket, key, local_parquet_path)
        print(f"Parquet file downloaded locally at {local_parquet_path}")

        # Load the Parquet file into a DataFrame
        df = pd.read_parquet(local_parquet_path)
        return df

    @staticmethod
    def save_parquet(df: pd.DataFrame, parquet_path: str):
        df.to_parquet(parquet_path, index=False)
        print(f"Parquet file saved at {parquet_path}")
