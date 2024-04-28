from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.langchain.models import DataIngestionStatusTableNew
from app.langchain.s3_doc_store import S3DocStore

# Assuming PARENT_CHUNKS_BUCKET_NAME is defined somewhere in your environment variables
PARENT_CHUNKS_BUCKET_NAME = 'poc-parent-document-retriever-docinsight'

class ContentFetcher:
    def __init__(self, db: Session):
        self.db = db
        self.docstore = S3DocStore(PARENT_CHUNKS_BUCKET_NAME)

    async def fetch_content_from_uuids_or_type(self, uuids: Optional[List[str]], content_type: Optional[str], request_id: Optional[str]):
        if uuids is None:
            # Fetch UUIDs from the database if no UUIDs are provided
            received_metadata = await self.fetch_uuids_from_db(request_id)
            uuids = []
            if content_type in ["images", "both"]:
                uuids.extend(received_metadata["images"])  # Add all image UUIDs
                uuids.extend(received_metadata["extra_image_uuid"])  # Add extra image UUIDs
            if content_type in ["tables", "both"]:
                uuids.extend(received_metadata["tables"])  # Add all table UUIDs

        content_list = await self.fetch_content_from_uuids(uuids)
        return content_list

    async def fetch_uuids_from_db(self, request_id: str):
        record = (
            self.db.query(DataIngestionStatusTableNew)
            .filter(DataIngestionStatusTableNew.request_id == request_id)
            .first()
        )
        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"No record found for request_id: {request_id}"
            )
        return record.table_figure_metadata

    async def fetch_content_from_uuids(self, uuids: List[str]):
        content_list = self.docstore.mmget(uuids)
        if not content_list or any(c is None for c in content_list):
            missing_uuids = [uuid for uuid, content in zip(uuids, content_list) if content is None]
            raise HTTPException(
                status_code=404,
                detail=f"Content not found for UUIDs: {missing_uuids}"
            )
        print("CONTENT IS", content_list)
        return [{"uuid": uuid, "actual_content": content} for uuid, content in zip(uuids, content_list)]
