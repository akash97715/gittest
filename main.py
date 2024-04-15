[Document(**json.loads(self.s3.get_object(Bucket=self.bucket, Key=f"{key}")["Body"].read())) for key in keys]
