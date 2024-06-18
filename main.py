def process_embeddings(add_embeddings_func, text_embeddings, metadatas, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            add_embeddings_func(text_embeddings=text_embeddings, metadatas=metadatas)
            logger.info("Successfully ingested all embeddings")
            break
        except BulkIndexError as e:
            retries += 1
            logger.error(f"BulkIndexError: {e.errors}")
            if retries >= max_retries:
                logger.error(f"Failed to index after {max_retries} retries")
            else:
                logger.info(f"Retrying, attempt {retries + 1}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            break
 
# Assuming add_embeddings is a method of an instantiated class, use `instance.add_embeddings`
# Replace `instance` with the actual instance of the class
embed_function=IASOpenaiEmbeddings(engine='text-embedding-ada-002',client_id='dummy',total_token_embedding=[],request=fastapi_request)
vector_db = IAS_OpenSearchVectorSearch(
    index_name="reingest22",
    embedding_function=embed_function,
    opensearch_url=AWS_OPENSEARCH_HOST,
    http_auth=(
        AWS_OPENSEARCH_USERNAME,
        AWS_OPENSEARCH_PASSWORD,
    ),
    is_aoss=False,
)
process_embeddings(vector_db.add_embeddings, text_embeddings, metadatas)
