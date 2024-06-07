POST /_reindex
{
  "source": {
    "index": "temp-restore-index"
  },
  "dest": {
    "index": "test-mapping-updated"
  }
}


PUT /test-mapping
{
  "settings": {
    "index": {
      "number_of_shards": 5,
      "knn.algo_param.ef_search": 512,
      "knn": true,
      "number_of_replicas": 1
    }
  },
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





PUT /_snapshot/biopharma-cosine-repository/biopharmacosine?wait_for_completion=true
{
"indices": "9cf1f92f762b222a1a72792a4c4ba9e9",
"ignore_unavailable": true,
"include_global_state": false,
"partial": false
}
