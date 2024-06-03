POST kibana_sample_data_ecommerce/_search
{
  "query": {
    "more_like_this": {
      "fields": ["docs"],
      "like": "what is there in docs",
      "min_term_freq": 1,
      "min_doc_freq": 1
    }
  }
}
