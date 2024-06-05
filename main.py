"vector_field": {
          "type": "knn_vector",
          "dimension": 1536,
          "method": {
            "engine": "nmslib",
            "space_type": "cosinesimil",
            "name": "hnsw",
            "parameters": {
              "ef_construction": 512,
              "m": 16
            }
          }
        }
