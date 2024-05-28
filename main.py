import asyncio
from app.base import IngestionPipeline

# Parameters
filename = "path/to/your/file.pdf"
chunk_size = 1000
chunk_overlap = 200
cust_metadata = {"key": "value"}
client_id = "your_client_id"
index_name = "your_index_name"
custom_extraction_document_path = "path/to/custom/extraction"
extract_images_tables = True
embed_raw_table = True
parent_document_chunk_size = 2000
parent_document_chunk_overlap = 400
separators = ["\n\n", "\n", " ", ""]
chunked_as_parent_child = True
advance_table_filter_flag = False
table_confidence_score = 20
s3_bucket = "your-s3-bucket"
s3_prefix = "your/s3/prefix"

# Additional keyword arguments (kwargs)
kwargs = {
    "splitter_type": "RCT"  # or "CTS" based on your requirement
}

# Create an instance of the IngestionPipeline class
pipeline = IngestionPipeline(
    filename=filename,
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    cust_metadata=cust_metadata,
    client_id=client_id,
    index_name=index_name,
    custom_extraction_document_path=custom_extraction_document_path,
    extract_images_tables=extract_images_tables,
    embed_raw_table=embed_raw_table,
    parent_document_chunk_size=parent_document_chunk_size,
    parent_document_chunk_overlap=parent_document_chunk_overlap,
    separators=separators,
    chunked_as_parent_child=chunked_as_parent_child,
    advance_table_filter_flag=advance_table_filter_flag,
    table_confidence_score=table_confidence_score,
    **kwargs
)

# Process the files asynchronously and save to Parquet
async def main():
    result = await pipeline.process_files()
    page_content = result["page_content"]
    metadata = result["metadata"]

    # Create an instance of the ParquetHelper class
    parquet_helper = ParquetHelper(page_content, metadata, s3_bucket, s3_prefix)
    
    # Create the Parquet file and get the S3 URI
    s3_uri = parquet_helper.create_parquet()
    print(f"Parquet file S3 URI: {s3_uri}")

# Run the async main function
asyncio.run(main())
