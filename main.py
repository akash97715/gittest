import pandas as pd
import boto3
import uuid
from typing import List

class ParquetHelper:
    def __init__(self, chunks: List[str], metadata: List[str], s3_bucket: str, s3_prefix: str):
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
