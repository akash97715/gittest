PUT /cosinesimilarity/_mapping
{
  "properties": {
    "vector_field": {
      "type": "knn_vector",
      "dimension": 1536,
      "method": {
        "name": "hnsw",
        "space_type": "cosinesimil",
        "engine": "nmslib",
        "parameters": {
          "ef_construction": 512,
          "m": 16
        }
      }
    }
  }
}
