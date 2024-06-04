PUT /cosinesimilarity/_mapping
{"properties": {"vector_field": {
          "type": "knn_vector",
          "dimension": 1536,
          "method": {
            "engine": "nmslib",
            "space_type": "l2",
            "name": "hnsw",
            "parameters": {
              "ef_construction": 512,
              "m": 16
            }
          }
        }}}
