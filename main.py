PUT /spacetype/_mapping
{
    "properties": {
        "new_field": {
            "type": "text"
        },
        "existing_field": {
            "type": "keyword",
            "ignore_above": 256
        }
    }
}
