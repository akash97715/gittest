from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.langchain.database import get_db
from app.langchain.content_fetcher import ContentFetcher  # Import the ContentFetcher class

router = APIRouter()

@router.post("/fetch-content", response_model=List[Dict[str, str]])
async def fetch_content(
    uuids: List[str] = None,
    content_type: str = None,
    request_id: str = None,
    db: Session = Depends(get_db)
):
    content_fetcher = ContentFetcher(db)  # Instantiate the ContentFetcher with the database session
    try:
        content_list = await content_fetcher.fetch_content_from_uuids_or_type(uuids, content_type, request_id)
        return content_list
    except HTTPException as e:
        # You can add more sophisticated error handling and logging here if needed
        raise HTTPException(status_code=e.status_code, detail=e.detail)

