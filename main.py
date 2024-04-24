import json
import boto3
from typing import Sequence, Tuple, TypeVar, List, Optional, Iterator

K = TypeVar('K')
V = TypeVar('V')

class Document:
    def to_dict(self):
        return vars(self)

    @classmethod
    def from_dict(cls, data: dict):
        # Ensure that this method reconstructs a Document from a dictionary
        return cls(**data)

class S3DocStore:
    def __init__(self, bucket_name: str):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name

    def serialize(self, obj):
        """Helper function to serialize objects to JSON."""
        if isinstance(obj, Document) or not isinstance(obj, str):
            return json.dumps(obj.to_dict())
        else:
            return json.dumps(obj)

    def deserialize(self, data):
        """Helper function to deserialize JSON to Python objects."""
        obj = json.loads(data)
        if isinstance(obj, dict) and 'title' in obj and 'content' in obj:
            # Assuming the Document has 'title' and 'content' keys
            return Document.from_dict(obj)
        return obj

    def mset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
        for key, document in key_value_pairs:
            self.s3.put_object(
                Body=self.serialize(document),
                Bucket=self.bucket,
                Key=str(key),
            )

    def mget(self, keys: Sequence[K]) -> List[Optional[V]]:
        results = []
        for key in keys:
            try:
                response = self.s3.get_object(Bucket=self.bucket, Key=str(key))
                body = response['Body'].read()
                results.append(self.deserialize(body))
            except self.s3.exceptions.NoSuchKey:
                results.append(None)  # Handle missing keys gracefully
        return results

    def mdelete(self, keys: Sequence[K]) -> None:
        for key in keys:
            self.s3.delete_object(Bucket=self.bucket, Key=str(key))

    def yield_keys(self, *, prefix: str | None = None) -> Iterator[str]:
        paginator = self.s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for item in page.get('Contents', []):
                yield item['Key']
