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
