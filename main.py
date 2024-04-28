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

    content_list = await fetch_content_from_uuids(uuids)
    return content_list

async def fetch_content_from_uuids(uuids: List[str]):
    content_list = []
    for uuid in uuids:
        content = await get_s3_content(uuid)  # Simulate fetching content from S3 using the UUID
        if content is None:
            raise HTTPException(
                status_code=404,
                detail=f"Content not found for UUID: {uuid}"
            )
        content_list.append({"uuid": uuid, "actual_content": content})
    return content_list

async def get_s3_content(uuid: str):
    # Simulated function to fetch content from S3; replace with actual S3 fetching logic
    return f"Simulated content for UUID {uuid}"
