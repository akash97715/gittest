   def mget(self, keys: Sequence[K]) -> List[Optional[V]]:
        """
        Module to fetch from S3 bucket
        """
        results=[]
        for key in keys:
            response=self.s3.get_object(Bucket=self.bucket, Key=f"{key}")
            body = response['Body'].read()
            document_data = json.loads(body)
            if isinstance(document_data, dict):
               return results.append(Document(**document_data))
            else:
              return results.append(json.loads(body))  # or handle as needed
