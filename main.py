GET example_index/_search
{
  "size": 10000,  // Adjust based on the maximum expected number of documents
  "track_total_hits": true,  // This ensures you get the exact count of total matches
  "query": {
    "match": {
      "metadata.request_id": "4547d927-df8b-45ea-bb69-f2578f89d5c6"
    }
  }
}
