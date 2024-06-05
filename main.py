PUT /test-mapping
{
  "mappings": {
    "properties": {
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
    }
  }
}
"settings": {
      "index": {
        "number_of_shards": "5",
        "knn.algo_param": {
          "ef_search": "512"
        },
        "provided_name": "cosinesimilarity",
        "knn": "true",
        "creation_date": "1717486629927",
        "number_of_replicas": "1",
        "uuid": "StnsNGhBRBK7-eEreRTdpQ",
        "version": {
          "created": "136267827"
        }
      }
