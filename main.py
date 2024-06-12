# Add to vectorDB
vector_db = IAS_OpenSearchVectorSearch(
                                    index_name="32dea38ed04635d9354625041c98a6e0",
                                    embedding_function=embd,
                                    opensearch_url=AWS_OPENSEARCH_HOST,
                                    http_auth=(
                                        AWS_OPENSEARCH_USERNAME,
                                        AWS_OPENSEARCH_PASSWORD,
                                    ),
                                    is_aoss=False,
                                )
retriever = vector_db.as_retriever()
