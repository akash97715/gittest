# fetch_doc_content/controller.py
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

async def fetch_content_from_uuids_or_type(uuids: Optional[List[str]], content_type: Optional[str], request_id: Optional[str], db: Session):
    if uuids is None:
        # Fetch UUIDs based on content_type and request_id from the database
        uuids = await fetch_uuids_from_db(content_type, request_id, db)

    content_list = []
    for uuid in uuids:
        content = await get_s3_content(uuid)
        if content is None:
            raise HTTPException(
                status_code=404,
                detail=f"Content not found for UUID: {uuid}"
            )
        content_list.append({"uuid": uuid, "actual_content": content})
    return content_list

async def fetch_uuids_from_db(content_type: str, request_id: str, db: Session):
    # Actual logic to fetch UUIDs based on content type and request ID from the database
    # Placeholder for database query
    # Example return:
    return ["uuid-from-db-1", "uuid-from-db-2"]

async def get_s3_content(uuid: str):
    # Implement actual logic to fetch content from S3 using the UUID
    return "Simulated content for UUID " + uuid
