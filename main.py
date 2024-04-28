from typing import Sequence, List, Optional
import json

class YourClassName:
    def __init__(self, bucket, s3):
        self.bucket = bucket
        self.s3 = s3

    def mget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        """
        Module to fetch from S3 bucket
        """
        results = []
        for key in keys:
            try:
                # Fetch the object
                response = self.s3.get_object(Bucket=self.bucket, Key=f"{key}")["Body"].read()
                # Attempt to parse the JSON
                document_data = json.loads(response)
                # Ensure the data is a dictionary for Document creation
                if isinstance(document_data, dict):
                    results.append(Document(**document_data))
                else:
                    # Handle non-dictionary data types (e.g., string)
                    results.append(None)  # or handle as needed
            except json.JSONDecodeError:
                # Handle JSON decode errors (e.g., when response is not a valid JSON string)
                results.append(None)
            except Exception as e:
                # Handle other exceptions such as S3 access issues, etc.
                results.append(None)
                print(f"Failed to fetch or parse document for key {key}: {str(e)}")

        return results
