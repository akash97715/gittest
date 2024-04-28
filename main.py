from typing import List, Dict, Optional
from fastapi import HTTPException

async def fetch_content_from_type(content_type: Optional[str], db_data: Dict):
    if content_type not in ["images", "tables", "both"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type provided: {content_type}. Must be 'images', 'tables', or 'both'."
        )
    
    uuids = []
    if content_type in ["images", "both"]:
        uuids.extend(db_data["images"])  # Add all image UUIDs
        uuids.extend(db_data["extra_image_uuid"])  # Add extra image UUIDs
    if content_type in ["tables", "both"]:
        uuids.extend(db_data["tables"])  # Add all table UUIDs

    content_list = await get_s3_content(uuids)
    return [{"uuid": uuid, "actual_content": content} for uuid, content in zip(uuids, content_list)]

async def get_s3_content(uuids: List[str]):
    # This function now fetches content for a list of UUIDs in one go; replace with actual S3 fetching logic
    # Simulate fetching multiple contents from S3 by returning a list with content for each UUID
    return [f"Simulated content for UUID {uuid}" for uuid in uuids]

