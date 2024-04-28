from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
 
from app.langchain.models import DataIngestionStatusTableNew
from app.langchain.database import get_db
from app.langchain.s3_doc_store import S3DocStore
 
#PARENT_CHUNKS_BUCKET_NAME = os.environ.get("PARENT_CHUNKS_BUCKET_NAME", "")
PARENT_CHUNKS_BUCKET_NAME='poc-parent-document-retriever-docinsight'  
docstore=S3DocStore(PARENT_CHUNKS_BUCKET_NAME)
 
async def fetch_content_from_uuids_or_type(uuids: Optional[List[str]], content_type: Optional[str], request_id: Optional[str], db: Session= Depends(get_db),):
    if uuids is None:
        # Fetch UUIDs based on content_type and request_id from the database
        received_metadata = await fetch_uuids_from_db(content_type, request_id, db)
    uuids = []
    if content_type in ["images", "both"]:
        uuids.extend(received_metadata["images"])  # Add all image UUIDs
        uuids.extend(received_metadata["extra_image_uuid"])  # Add extra image UUIDs
    if content_type in ["tables", "both"]:
        uuids.extend(received_metadata["tables"])  # Add all table UUIDs
 
    content_list = await fetch_content_from_uuids(uuids)        
 
    return content_list
 
 
 
async def fetch_uuids_from_db(request_id: str, db: Session):
    record = (
        db.query(DataIngestionStatusTableNew)
        .filter(
            DataIngestionStatusTableNew.request_id == request_id
           
        )
        .first()
    )
    received_metadata=record.table_figure_metadata
 
    return received_metadata    
 
 
 
async def fetch_content_from_uuids(uuids: List[str]):
    # Fetch content from the document store using a multi-get operation
    content_list = docstore.mmget(uuids)
 
    # Check if the content list is empty or contains any None values (indicating missing content for some UUIDs)
    if not content_list or any(c is None for c in content_list):
        # Optionally, identify which UUIDs were not found
        missing_uuids = [uuid for uuid, content in zip(uuids, content_list) if content is None]
        raise HTTPException(
            status_code=404,
            detail=f"Content not found for UUIDs: {missing_uuids}"
        )
 
    # Logging the content for debugging purposes
    print("CONTENT IS", content_list)
 
    # Return a list of dictionaries mapping each UUID to its corresponding content
    return [{"uuid": uuid, "actual_content": content} for uuid, content in zip(uuids, content_list)]
