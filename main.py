import aioboto3
import json
from langchain_core.stores import BaseStore
from langchain_core.documents import Document
from typing import Optional, List, Iterator, Sequence, Tuple, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class S3DocStore(BaseStore):
    """
    Class with modules to store, fetch & delete parent chunks to/from S3 bucket
    """
 
    def __init__(self, bucket_name):
        self.bucket = bucket_name

    async def _serialize(self, obj):
        """Helper function to serialize objects to JSON."""
        if isinstance(obj, Document) or not isinstance(obj, str):
            return json.dumps(dict(obj))
        else:
            return json.dumps(obj)
 
    async def mset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
        """
        Module to store in S3 bucket
        """
        async with aioboto3.client("s3") as s3:
            for key, document in key_value_pairs:
                await s3.put_object(
                    Body=json.dumps(dict(document)),
                    Bucket=self.bucket,
                    Key=f"{key}",
                )

    async def mmset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
        async with aioboto3.client("s3") as s3:
            for key, document in key_value_pairs:
                body = await self._serialize(document)
                await s3.put_object(
                    Body=body,
                    Bucket=self.bucket,
                    Key=str(key),
                )
 
    async def mget(self, keys: Sequence[K]) -> List[Optional[V]]:
        """
        Module to fetch from S3 bucket
        """
        results = []
        async with aioboto3.client("s3") as s3:
            for key in keys:
                response = await s3.get_object(Bucket=self.bucket, Key=f"{key}")
                body = await response['Body'].read()
                document = Document(**json.loads(body))
                results.append(document)
        return results

    async def mmget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        """
        Module to fetch from S3 bucket
        """
        results = []
        async with aioboto3.client("s3") as s3:
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
        async with aioboto3.client("s3") as s3:
            for key in keys:
                await s3.delete_object(Bucket=self.bucket, Key=key)
 
    async def yield_keys(
        self, *, prefix: str | None = None
    ) -> Iterator | Iterator[str]:
        pass
