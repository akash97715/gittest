# Sample data structure as provided earlier
data = {
    "images": [
        "885ba9df6be84f57b0fcd50b9220a91536123/ae298e960dd36928c58a407fd87fbf8a/35390b40-ca06-4c19-84b1-d654454b497b",
        # Additional images...
    ],
    "tables": [
        "885ba9df6be84f57b0fcd50b9220a91536123/ae298e960dd36928c58a407fd87fbf8a/a910180c-c6bb-40cd-a5ab-c9aafec2cf95",
        # Additional tables...
    ],
    "extra_image_data": [
        # Extra image metadata entries...
    ],
    "extra_table_data": [
        # Extra table metadata entries...
    ]
}

# Function to find metadata for a given UUID from any extra data
def find_metadata(uuid, extra_data_list):
    for extra_data in extra_data_list:
        for item in extra_data:
            if item['id_key'] == uuid:
                return item
    return None

# Create a list of images with their metadata
image_metadata_list = []
for image in data['images']:
    metadata = find_metadata(image, [data['extra_image_data'], data['extra_table_data']])
    if metadata:
        image_metadata_list.append({'uuid': image, 'metadata': metadata})

# Create a list of tables with their metadata
table_metadata_list = []
for table in data['tables']:
    metadata = find_metadata(table, [data['extra_image_data'], data['extra_table_data']])
    if metadata:
        table_metadata_list.append({'uuid': table, 'metadata': metadata})

# Combine both lists if needed or handle them separately
combined_metadata_list = image_metadata_list + table_metadata_list

# Output the combined list of dictionaries containing UUIDs and their metadata
print(combined_metadata_list)
