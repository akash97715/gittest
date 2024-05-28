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
