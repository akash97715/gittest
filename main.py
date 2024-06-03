POST kibana_sample_data_ecommerce/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "docs": "what is there in docs"
          }
        }
      ],
      "filter": [
        {
          "term": {
            "metadata.md5": "7268768"
          }
        }
      ]
    }
  }
}
