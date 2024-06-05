POST _snapshot/your-repository-name/dev-snapshot/_restore?wait_for_completion=true
{
"indices": "Indexname-1, index-name2",
"include_global_state": false
}
