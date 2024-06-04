if large_file:
    for i in range(0, len(page_content)):
        vectors = vector_db_ingestion.add_texts(
            texts=page_content[i], metadatas=metadata[i],kwargs=
        )
