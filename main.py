from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Body, Query, Depends
from sqlalchemy.orm import Session
from my_app.dependencies import async_token_validation_and_metering, get_s3_content, get_db

router = APIRouter()

@router.post(
    "/fetch-content",
    status_code=200,
    tags=["Content Fetcher"],
    description="This endpoint fetches content from S3 based on direct UUIDs or a content type query, returning the actual content.",
    response_model=List[Dict[str, str]]
)
@async_token_validation_and_metering()
async def fetch_content(
    uuids: Optional[List[str]] = Body(default=None),
    content_type: Optional[str] = Query(default=None, description="Type of content to fetch: 'tables', 'images', or 'both'"),
    db: Session = Depends(get_db)
):
    try:
        if uuids is None and content_type is None:
            raise HTTPException(
                status_code=400,
                detail="Either UUIDs or content type must be provided."
            )

        if uuids is None:
            # Fetch UUIDs from database based on content type
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
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching content: {str(e)}"
        )

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
