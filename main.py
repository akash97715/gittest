    async def mmget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        """
        Module to fetch from S3 bucket
        """
        results = []
        async with self.session.client("s3") as s3:
            for key in keys:
                response = await s3.get_object(Bucket=self.bucket, Key=f"{key}")
                body = await response['Body'].read()
                document_data = json.loads(body)
                if isinstance(document_data, dict):
                    results.append(Document(**document_data))
                else:
                    results.append(json.loads(body))  # or handle as needed
        return results
