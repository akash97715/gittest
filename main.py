from typing import List, Optional, Sequence, TypeVar, Generic
import json

K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type (assuming V can be a Document or parsed JSON data)

class S3BucketHandler(Generic[K, V]):
    def __init__(self, s3_client, bucket_name):
        self.s3 = s3_client
        self.bucket = bucket_name

    def mget(self, keys: Sequence[K]) -> List[Optional[V]]:
        """
        Fetch multiple items from an S3 bucket.
        
        Args:
            keys (Sequence[K]): A sequence of keys to fetch objects for.

        Returns:
            List[Optional[V]]: A list of parsed JSON data or Document instances,
                                corresponding to each key. None is appended if an error occurs.
        """
        results = []
        for key in keys:
            try:
                response = self.s3.get_object(Bucket=self.bucket, Key=str(key))
                body = response['Body'].read()
                document_data = json.loads(body)
                if isinstance(document_data, dict):
                    # Assuming Document is a class that can be initialized with keyword arguments
                    results.append(Document(**document_data))
                else:
                    # If document_data is not a dict, append it directly (could be a list or a plain type)
                    results.append(document_data)
            except Exception as e:
                # Handle exceptions such as the object not existing or other AWS errors
                print(f"Error fetching object {key}: {e}")
                results.append(None)  # Append None or handle as needed

        return results
