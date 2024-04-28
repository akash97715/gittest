from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from .controller import ContentFetcher
from validator.decorators import async_token_validation_and_metering
from app.langchain.database import get_db
from fastapi import Request as fastapi_request

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
    request: fastapi_request,
    uuids_request: UUIDsRequest = Body(default=None),  # Using the Pydantic model for the body
    content_type: Optional[str] = Query(default=None, description="Type of content to fetch: 'tables', 'images', or 'both'."),
    request_id: Optional[str] = Query(default=None, description="Request ID associated with the content type."),
    db: Session = Depends(get_db)
):
    client_id = request.headers.get("x-agw-client_id")
    if not client_id:
        raise HTTPException(
            status_code=400, detail="Client Id is not sent in headers"
        )  
    content_fetcher = ContentFetcher(db)  # Instantiate the ContentFetcher with the database session
    try:
        # Passing parameters to the content fetcher function
        content_list = await content_fetcher.fetch_content_from_uuids_or_type(
            uuids_request.uuids, 
            content_type, 
            request_id
        )
        return content_list
    except HTTPException as e:
        # More sophisticated error handling and logging could be added here
        raise HTTPException(status_code=e.status_code, detail=e.detail)
