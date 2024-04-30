async def mset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
       
        """
        Module to store in S3 bucket
        """
        async with self.session.client("s3") as s3:
            for key, document in key_value_pairs:
                body = await self._serialize(document)
                await s3.put_object(
                    Body=body,
                    Bucket=self.bucket,
                    Key=str(key),
                )
