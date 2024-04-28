import boto3
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
        self.s3 = boto3.client("s3")
        self.bucket = bucket_name
 
    def _serialize(self, obj):
        """Helper function to serialize objects to JSON."""
        if isinstance(obj, Document) or not isinstance(obj, str):
            return json.dumps(dict(obj))
        else:
            return json.dumps(obj)
 
    def mset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
        """
        Module to store in S3 bucket
        """
        for key, document in key_value_pairs:
            self.s3.put_object(
                Body=json.dumps(dict(document)),
                Bucket=self.bucket,
                Key=f"{key}",
            )
    def mmset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
        for key, document in key_value_pairs:
            self.s3.put_object(
                Body=self._serialize(document),
                Bucket=self.bucket,
                Key=str(key),
            )
 
    def mget(self, keys: Sequence[K]) -> List[Optional[V]]:
        """
        Module to fetch from S3 bucket
        """
        return [
            Document(
                **json.loads(
                    self.s3.get_object(
                        Bucket=self.bucket, Key=f"{key}"
                    )["Body"].read()
                )
            )
            for key in keys
        ]
    def mmget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        """
        Module to fetch from S3 bucket
        """
        results = []
        for key in keys:
           
            # Fetch the object
            response = self.s3.get_object(Bucket=self.bucket, Key=f"{key}")["Body"].read()
            # Attempt to parse the JSON
            document_data = json.loads(response)
            # Ensure the data is a dictionary for Document creation
            if isinstance(document_data, dict):
                results.append(Document(**document_data))
            else:
                # Handle non-dictionary data types (e.g., string)
                results.append(json.loads(response)) # or handle as needed
           
 
        return results
 
    def mdelete(self, keys: Sequence) -> None:
        """
        Module to delete from S3 bucket
        """
        for key in keys:
            self.s3.delete_object(Bucket=self.bucket, key=key)
 
    def yield_keys(
        self, *, prefix: str | None = None
    ) -> Iterator | Iterator[str]:
        pass
has context menu
