PUT /my_index/_mapping
{
    "properties": {
        "vector_field": {
            "type": "nested",
            "properties": {
                "space_type": {
                    "type": "nested",
                    "properties": {
                        "new_property": {
                            "type": "text"
                        },
                        "existing_property": {
                            "type": "integer",
                            "null_value": 0  // Example of modifying an existing property
                        }
                    }
                }
            }
        }
    }
}
