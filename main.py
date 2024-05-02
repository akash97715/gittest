from typing import Optional, List
from fastapi import HTTPException

class YourServiceClass:
    # Assuming other necessary imports and class attributes are defined
    
    async def fetch_content_from_uuids_or_type(self, uuids: Optional[List[str]], content_type: Optional[str], request_id: Optional[str]):
        if uuids is None:
            # Fetch UUIDs and metadata from the database if no UUIDs are provided
            received_metadata = await self.fetch_uuids_from_db(request_id)
            uuids = []
            metadata_list = []
            if content_type in ["images", "both"]:
                uuids.extend(received_metadata["images"])  # Add all image UUIDs
                uuids.extend(received_metadata["extra_image_uuid"])  # Add extra image UUIDs
                metadata_list.extend(received_metadata["extra_image_data"])
            if content_type in ["tables", "both"]:
                uuids.extend(received_metadata["tables"])  # Add all table UUIDs
                metadata_list.extend(received_metadata["extra_table_data"])
            
        content_list = await self.fetch_content_from_uuids(uuids)
        return self.append_metadata_to_content(content_list, metadata_list)

    async def fetch_uuids_from_db(self, request_id: str):
        record = (
            self.db.query(DataIngestionStatusTableNew)
            .filter(DataIngestionStatusTableNew.request_id == request_id)
            .first()
        )
        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"No record found for request_id: {request_id}"
            )
        return record.table_figure_metadata
 
    async def fetch_content_from_uuids(self, uuids: List[str]):
        content_list = await self.docstore.mmget(uuids)
        if not content_list or any(c is None for c in content_list):
            missing_uuids = [uuid for uuid, content in zip(uuids, content_list) if content is None]
            raise HTTPException(
                status_code=404,
                detail=f"Content not found for UUIDs: {missing_uuids}"
            )
        return [{"uuid": uuid, "actual_content": content} for uuid, content in zip(uuids, content_list)]

    def append_metadata_to_content(self, content_list, metadata_list):
        # Mapping metadata to UUIDs
        metadata_map = {meta['id_key']: meta for meta in metadata_list}
        for item in content_list:
            uuid = item['uuid']
            # Append metadata to the content list where UUIDs match
            if uuid in metadata_map:
                item['metadata'] = metadata_map[uuid]
        return content_list

