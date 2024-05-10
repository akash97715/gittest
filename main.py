def append_metadata_to_content(self, content_list, metadata_list):
    # Sort metadata list by 'filename' and 'pagenumber' 
    metadata_list.sort(key=lambda x: (x['filename'], x['pagenumber']))

    # Mapping metadata to UUIDs
    metadata_map = {meta['docinsight_custom_extraction_id_key']: meta for meta in metadata_list}
    
    # Append metadata to the content list where UUIDs match
    for item in content_list:
        uuid = item['uuid']
        if uuid in metadata_map:
            item['metadata'] = metadata_map[uuid]
    
    return content_list
