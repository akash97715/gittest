from langchain_core.stores import BaseStore
from typing import Iterator, Sequence, Tuple, TypeVar
from langchain_core.documents import  Document
import json
K = TypeVar("K")
V = TypeVar("V")
 
import boto3
 
class S3DocStore(BaseStore):
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name
 
    def mset(self, key_value_pairs: Sequence[Tuple[K, V]])->None:
        for key, document in key_value_pairs:
            print("the key is",key)
            self.s3.put_object(
                Body=json.dumps(dict(document)),
                Bucket=self.bucket,
                Key=f"{key}",
            )
 
    def mget(self, keys: Sequence[K])-> List[Optional[V]]:
        print("the retreived keys are",keys)
        return  [Document(**json.loads(self.s3.get_object(Bucket=self.bucket, Key=f"{key}")["Body"].read())) for key in keys]
   
    def mdelete(self, keys: Sequence) -> None:
        for key in keys:
            self.s3.delete_object(Bucket=self.bucket, key=key)
 
    def yield_keys(self, *, prefix: str | None = None) -> Iterator | Iterator[str]:
        pass
