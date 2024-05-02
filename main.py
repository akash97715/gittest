# fetch_doc_content/router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from .controller import ContentFetcher
from sqlalchemy.orm import Session
from validator.decorators import async_token_validation_and_metering
from app.langchain.database import get_db
from fastapi import Request as fastapi_request
from fastapi import APIRouter, Depends, Body, Query, HTTPException
from app.langchain.v1.models import  UUIDsRequest
 
 
 
 
router = APIRouter()
 
@router.post(
    "/fetch-doc-content",
    status_code=200,
    tags=["Content Fetcher"],
    description="This endpoint fetches content from S3 based on direct UUIDs or a combination of content type and request ID, returning the actual content.",
    response_model=List[Dict]
)
@async_token_validation_and_metering()
async def fetch_content_endpoint(
    request: fastapi_request,
    uuids_request: UUIDsRequest = Body(default=None),  # Using the Pydantic model for the body
 
    db: Session = Depends(get_db)
):
    client_id = request.headers.get("x-agw-client_id")
    if not client_id:
        raise HTTPException(
            status_code=400, detail="Client Id is not sent in headers"
        )  
    content_fetcher = ContentFetcher(db)  # Instantiate the ContentFetcher with the database session
    uuids=uuids_request.contentuuidpath if uuids_request else None
    try:
        # Passing parameters to the content fetcher function
        content_list = await content_fetcher.fetch_content_from_uuids_or_type(
            uuids,
            uuids_request.content_type,
            uuids_request.request_id
        )
        return content_list
    except HTTPException as e:
        # More sophisticated error handling and logging could be added here
        raise HTTPException(status_code=e.status_code, detail=e.detail)
