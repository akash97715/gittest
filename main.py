# fetch_doc_content/router.py
from fastapi import APIRouter, Depends
from typing import List, Dict, Optional
from .controller import fetch_content_from_uuids_or_type
from my_app.dependencies import async_token_validation_and_metering, get_db

router = APIRouter()

@router.post(
    "/fetch-content",
    status_code=200,
    tags=["Content Fetcher"],
    description="This endpoint fetches content from S3 based on direct UUIDs or a content type query, returning the actual content.",
    response_model=List[Dict[str, str]]
)
@async_token_validation_and_metering()
async def fetch_content_endpoint(
    uuids: Optional[List[str]] = None,
    content_type: Optional[str] = None,
    db=Depends(get_db)
):
    return await fetch_content_from_uuids_or_type(uuids, content_type, db)
