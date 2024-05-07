GET example_index/_search
{
  "query": {
    "term": {
      "metadata.request_id.keyword": {
        "value": "4547d927-df8b-45ea-bb69-f2578f89d5c6"
      }
    }
  }
}
