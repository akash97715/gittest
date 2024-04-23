import json
import boto3
from typing import Sequence, Tuple, TypeVar, List, Optional, Iterator

K = TypeVar('K')
V = TypeVar('V')

class Document:
    # Ensure this method is present in the Document class
    def to_dict(self):
        return vars(self)

class S3DocStore:
    def __init__(self, bucket_name: str):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name

    def serialize(self, obj):
        """Helper function to serialize objects to JSON."""
        if isinstance(obj, Document):
            return json.dumps(obj.to_dict())
        else:
            return json.dumps(obj)

    def deserialize(self, data):
        """Helper function to deserialize JSON to Python objects."""
        # Implement logic here if you need to deserialize into Document objects
        return json.loads(data)

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
