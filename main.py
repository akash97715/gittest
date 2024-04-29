import asyncio
import json
from typing import List, Optional, Sequence

class YourClass:
    def __init__(self, session, bucket):
        self.session = session
        self.bucket = bucket

    async def fetch_object(self, s3, key: str) -> Optional[Document]:
        """
        Asynchronously fetch a single object from S3 and parse it into a Document.
        """
        response = await s3.get_object(Bucket=self.bucket, Key=key)
        body = await response['Body'].read()
        document_data = json.loads(body)
        if isinstance(document_data, dict):
            return Document(**document_data)
        else:
            return document_data  # or handle as needed based on your structure

    async def mmget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        """
        Module to fetch multiple documents from S3 bucket using asyncio.gather.
        """
        async with self.session.client("s3") as s3:
            # Gather all fetch tasks
            tasks = [self.fetch_object(s3, key) for key in keys]
            results = await asyncio.gather(*tasks)
        return results
