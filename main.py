    def append_metadata_to_content(self, content_list, metadata_list):
        # Mapping metadata to UUIDs
        metadata_map = {meta['docinsight_custom_extraction_id_key']: meta for meta in metadata_list}
        for item in content_list:
            uuid = item['uuid']
            # Append metadata to the content list where UUIDs match
            if uuid in metadata_map:
                item['metadata'] = metadata_map[uuid]
        return content_list
