kl = vector_db.similarity_search(
    test_query,
    kwargs={
        "filter": {
            "terms": {
                "metadata.md5": ["3863033b4e4ff29fe6125b2d2efcae9e"]
            }
        },
        "k": 400
    }
)


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


kl = vector_db.similarity_search(
    test_query,
    kwargs={
        "filter": {
            "bool": {
                "filter": [
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


import json

filter_query = {
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

print(json.dumps(filter_query, indent=2))

kl = vector_db.similarity_search(test_query, kwargs=filter_query)
