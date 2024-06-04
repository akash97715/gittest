from opensearchpy import OpenSearch

# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('user', 'password'),  # Use your OpenSearch username and password
    use_ssl=True,  # Set to False if not using SSL
    verify_certs=True,  # Set to False if not verifying SSL certificates
    connection_class=RequestsHttpConnection
)

# Define the index and query
index_name = 'your-index-name'
query = {
    "query": {
        "match_all": {}
    },
    "_source": ["vector_field"]  # Replace with the actual field name that stores the vectors
}

# Execute the search query
response = client.search(index=index_name, body=query)

# Extract vectors from the search results
vectors = []
for hit in response['hits']['hits']:
    vector = hit['_source']['vector_field']  # Replace with the actual field name
    vectors.append(vector)

# Print the vectors
for vector in vectors:
    print(vector)

# Alternatively, store vectors in a list
vector_list = [hit['_source']['vector_field'] for hit in response['hits']['hits']]
