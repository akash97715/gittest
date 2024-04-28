# fetch_doc_content/controller.py
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

async def fetch_content_from_uuids_or_type(uuids: Optional[List[str]], content_type: Optional[str], db: Session):
    if uuids is None and content_type is None:
        raise HTTPException(
            status_code=400,
            detail="Either UUIDs or content type must be provided."
        )

    if uuids is None:
        uuids = await fetch_uuids_from_db(content_type, db)

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

async def fetch_uuids_from_db(content_type: str, db: Session):
    # Implement actual logic to fetch UUIDs based on the content type from the database
    if content_type == "tables":
        return ["uuid-for-table-1", "uuid-for-table-2"]
    elif content_type == "images":
        return ["uuid-for-image-1", "uuid-for-image-2"]
    elif content_type == "both":
        return ["uuid-for-table-1", "uuid-for-table-2", "uuid-for-image-1", "uuid-for-image-2"]
    else:
        raise ValueError("Invalid content type provided")

async def get_s3_content(uuid: str):
    # Replace this with actual logic to fetch content from S3 using the UUID
    return "Simulated content for UUID " + uuid
