import uuid

client_id = 'LDPTRU'  # Example client_id
index_name = 'your_index_name'

id_key = "{}/{}/{}".format(
    client_id if not (len(client_id) == 36 and all(c in '0123456789abcdef-' for c in client_id.lower())) else str(uuid.UUID(client_id)), 
    index_name, 
    uuid.uuid4()
)

print(id_key)
