# Example data to update
data = [
    { "update": { "_id": "1", "_index": "example_index" }},
    { "doc": { "field_to_update": "new_value" }},
    { "update": { "_id": "2", "_index": "example_index" }},
    { "doc": { "field_to_update": "another_new_value" }}
]



from opensearchpy.helpers import bulk

# Function to format the data for the bulk API
def generate_bulk_data(data):
    for item in data:
        yield item

# Performing the bulk update
success, failed = bulk(client, generate_bulk_data(data))

print(f"Successfully updated {success} documents, {failed} failed.")
