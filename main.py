POST /_snapshot/biopharma-cosine-repository/biopharmacosine/_restore?wait_for_completion=true
{
  "indices": "9cf1f92f762b222a1a72792a4c4ba9e9",  // original index name in the snapshot
  "include_global_state": false,
  "rename_pattern": "9cf1f92f762b222a1a72792a4c4ba9e9",  // original index name in the snapshot
  "rename_replacement": "test-mapping-updated"  // new index name
}
