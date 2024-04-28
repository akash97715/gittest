# fetch_doc_content/router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from .controller import ContentFetcher
from validator.decorators import async_token_validation_and_metering
from app.langchain.database import get_db
from fastapi import Request as fastapi_request
from fastapi import APIRouter, Depends, Body, Query, HTTPException
 
 
 
router = APIRouter()
 
@router.post(
    "/fetch-content",
    status_code=200,
    tags=["Content Fetcher"],
    description="This endpoint fetches content from S3 based on direct UUIDs or a combination of content type and request ID, returning the actual content.",
    response_model=List[Dict]
)
@async_token_validation_and_metering()
async def fetch_content_endpoint(
    request:fastapi_request,
    uuids: Optional[List[str]] = Body(default=None, description="A list of UUIDs to fetch content for."),
    content_type: Optional[str] = Query(default=None, description="Type of content to fetch: 'tables', 'images', or 'both'."),
    request_id: Optional[str] = Query(default=None, description="Request ID associated with the content type."),
    db=Depends(get_db)
):
    client_id = (
        request.headers.get("x-agw-client_id")
        if request.headers.get("x-agw-client_id") is not None
        else None
    )
 
    if not client_id:
        raise HTTPException(
            status_code=400, detail="Client Id is not sent in headers"
        )  
    content_fetcher = ContentFetcher(db)  # Instantiate the ContentFetcher with the database session
    try:
        content_list = await content_fetcher.fetch_content_from_uuids_or_type(uuids, content_type, request_id)
        return content_list
    except HTTPException as e:
        # You can add more sophisticated error handling and logging here if needed
        raise HTTPException(status_code=e.status_code, detail=e.detail)
