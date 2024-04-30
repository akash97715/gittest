import asyncio
from concurrent.futures import ThreadPoolExecutor
import aioboto3
import json
from langchain_core.stores import BaseStore
from langchain_core.documents import Document
from typing import Optional, List, Sequence, Tuple, TypeVar
import boto3

K = TypeVar("K")
V = TypeVar("V")

class S3DocStore(BaseStore):
    def __init__(self, bucket_name):
        self.bucket = bucket_name
        self.s3 = boto3.client("s3")
        self.session = aioboto3.Session()

    async def _serialize(self, obj):
        if isinstance(obj, Document) or not isinstance(obj, str):
            return json.dumps(dict(obj))
        else:
            return json.dumps(obj)

    async def mset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
        async with self.session.client("s3") as s3:
            tasks = [asyncio.create_task(self.put_object_async(s3, key, document))
                     for key, document in key_value_pairs]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    async def put_object_async(self, s3, key, document):
        body = await self._serialize(document)
        return await s3.put_object(Body=body, Bucket=self.bucket, Key=str(key))

    async def mget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        results = []
        async with self.session.client("s3") as s3:
            tasks = [asyncio.create_task(self.get_object_async(s3, key)) for key in keys]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            results = [task.result() for task in done if task.result() is not None]
        return results

    async def get_object_async(self, s3, key):
        try:
            response = await s3.get_object(Bucket=self.bucket, Key=f"{key}")
            body = await response['Body'].read()
            document_data = json.loads(body)
            if isinstance(document_data, dict):
                return Document(**document_data)
            else:
                return json.loads(body)  # or handle as needed
        except Exception as e:
            return None  # Handle exceptions or log errors as necessary

    async def mdelete(self, keys: Sequence) -> None:
        async with self.session.client("s3") as s3:
            for key in keys:
                await s3.delete_object(Bucket=self.bucket, Key=key)

    async def yield_keys(self, *, prefix: str | None = None) -> Iterator | Iterator[str]:
        pass
