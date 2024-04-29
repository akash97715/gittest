from typing import List, Optional, Sequence
import json
from concurrent.futures import ThreadPoolExecutor

class YourClass:
    def __init__(self, s3, bucket):
        self.s3 = s3
        self.bucket = bucket

    def fetch_object(self, key):
        """
        Fetch a single object from S3 and parse it into a Document.
        """
        response = self.s3.get_object(Bucket=self.bucket, Key=str(key))
        body = response["Body"].read()
        return Document(**json.loads(body))

    def mget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        """
        Module to fetch multiple documents from S3 bucket using ThreadPoolExecutor.
        """
        with ThreadPoolExecutor() as executor:
            # Map fetch_object to each key and convert results to list
            documents = list(executor.map(self.fetch_object, keys))
        return documents
