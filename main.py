# fetch_doc_content/router.py
from fastapi import APIRouter, Depends, Body, Query, HTTPException
from typing import List, Dict, Optional
from .controller import fetch_content_from_uuids_or_type
from my_app.dependencies import async_token_validation_and_metering, get_db

router = APIRouter()

@router.post(
    "/fetch-content",
    status_code=200,
    tags=["Content Fetcher"],
    description="This endpoint fetches content from S3 based on direct UUIDs or a combination of content type and request ID, returning the actual content.",
    response_model=List[Dict[str, str]]
)
@async_token_validation_and_metering()
async def fetch_content_endpoint(
    uuids: Optional[List[str]] = Body(default=None, description="A list of UUIDs to fetch content for."),
    content_type: Optional[str] = Query(default=None, description="Type of content to fetch: 'tables', 'images', or 'both'."),
    request_id: Optional[str] = Query(default=None, description="Request ID associated with the content type."),
    db=Depends(get_db)
):
    if (uuids is None and (content_type is None or request_id is None)) or (uuids and (content_type or request_id)):
        raise HTTPException(
            status_code=400,
            detail="Either provide a list of UUIDs, or both content_type and request_id must be provided together."
        )
    return await fetch_content_from_uuids_or_type(uuids, content_type, request_id, db)
