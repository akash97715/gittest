import asyncio
from concurrent.futures import ThreadPoolExecutor
import aioboto3
import json
from langchain_core.stores import BaseStore
from langchain_core.documents import Document
from typing import Optional, List, Iterator, Sequence, Tuple, TypeVar
import boto3
 
K = TypeVar("K")
V = TypeVar("V")
 
class S3DocStore(BaseStore):
    """
    Class with modules to store, fetch & delete parent chunks to/from S3 bucket
    """
    def __init__(self, bucket_name):
        self.bucket = bucket_name
        self.s3 = boto3.client("s3")
        self.session=  aioboto3.Session()
 
    async def _serialize(self, obj):
        """Helper function to serialize objects to JSON."""
        if isinstance(obj, Document) or not isinstance(obj, str):
            return json.dumps(dict(obj))
        else:
            return json.dumps(obj)
    async def mset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
        """
        Asynchronously store multiple key-value pairs in an S3 bucket, handling tasks using asyncio.wait.
        """
        async with self.session.client("s3") as s3:
            tasks = [asyncio.create_task(self.put_object_async(s3, key, document))
                     for key, document in key_value_pairs]
 
            # Wait for all tasks to complete
            done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            # You can handle done and pending tasks here if needed
    async def put_object_async(self, s3, key, document):
        """
        Serialize and upload a document to an S3 bucket asynchronously.
        """
        body = await self._serialize(document)
        return await s3.put_object(Body=body, Bucket=self.bucket, Key=str(key))
 
 
   
 
    async def mget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        """
        Module to fetch from S3 bucket
        """
        results = []
        async with self.session.client("s3") as s3:
            for key in keys:
                response = await s3.get_object(Bucket=self.bucket, Key=f"{key}")
                body = await response['Body'].read()
                document_data = json.loads(body)
                if isinstance(document_data, dict):
                    results.append(Document(**document_data))
                else:
                    results.append(json.loads(body))  # or handle as needed
        return results
    async def mdelete(self, keys: Sequence) -> None:
        """
        Module to delete from S3 bucket
        """
        async with self.session.client("s3") as s3:
            for key in keys:
                await s3.delete_object(Bucket=self.bucket, Key=key)
    async def yield_keys(
        self, *, prefix: str | None = None
    ) -> Iterator | Iterator[str]:
        pass
