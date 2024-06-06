import uuid

client_id = 'your_client_id_or_uuid'
index_name = 'your_index_name'

id_key = "{}/{}/{}".format(
    client_id if client_id.isdigit() else str(uuid.UUID(client_id)), 
    index_name, 
    uuid.uuid4()
)

print(id_key)
