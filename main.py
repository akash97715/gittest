def append_metadata_to_content(self, content_list, metadata_list):
    # Mapping metadata to UUIDs
    metadata_map = {meta['docinsight_custom_extraction_id_key']: meta for meta in metadata_list}
    
    # Create a new list that includes metadata with each content item if available
    content_with_metadata = [
        {**item, 'metadata': metadata_map.get(item['uuid'], {})} for item in content_list
    ]

    # Sort the content list by 'filename' and 'pagenumber' in metadata, handling missing metadata
    content_with_metadata.sort(key=lambda x: (
        x['metadata'].get('filename', ''), x['metadata'].get('pagenumber', 0)
    ))

    return content_with_metadata
