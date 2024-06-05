PUT /_snapshot/biopharma-cosine-repository/biopharmacosine?wait_for_completion=true
{
"indices": "9cf1f92f762b222a1a72792a4c4ba9e9",
"ignore_unavailable": true,
"include_global_state": false,
"partial": false
}
 
 
POST _snapshot/biopharma-cosine-repository/biopharmacosine/_restore?wait_for_completion=true
{
"indices": "test-mapping-updated",
"include_global_state": false
}
