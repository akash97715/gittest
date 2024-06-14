from parquet_embedding_processor import ParquetEmbeddingProcessor  # Ensure the import path is correct

# Example data for initialization
chunks = ["text chunk 1", "text chunk 2", "text chunk 3"]
metadata = ["metadata 1", "metadata 2", "metadata 3"]
s3_bucket = "your-s3-bucket-name"
s3_prefix = "your/s3/prefix"
engine = "your-openai-engine"
client_id = "your-client-id"
x_vsl_client_id = "your-x-vsl-client-id"

# Step 1: Create and upload Parquet file
processor = ParquetEmbeddingProcessor(
    chunks=chunks,
    metadata=metadata,
    s3_bucket=s3_bucket,
    s3_prefix=s3_prefix
)

s3_uri = processor.create_parquet()
print(f"Parquet file uploaded to: {s3_uri}")

# Step 2: Download and process Parquet file with embeddings
processor = ParquetEmbeddingProcessor(
    parquet_path=s3_uri,
    engine=engine,
    client_id=client_id,
    x_vsl_client_id=x_vsl_client_id,
    bearer_token="your-bearer-token"  # Or use the federate_auth method to get the token
)

processor.process_parquet()
print("Parquet file processed and updated.")
