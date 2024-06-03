kl = vector_db.similarity_search(
    test_query,
    kwargs={
        "filter": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "metadata.md5": ["3863033b4e4ff29fe6125b2d2efcae9e"]
                        }
                    }
                ]
            }
        },
        "k": 400
    }
)
