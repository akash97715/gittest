def mset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
        for key, document in key_value_pairs:
            print("the key is", key)
            self.s3.put_object(
                Body=json.dumps(dict(document)),
                Bucket=self.bucket,
                Key=f"{key}",
            )
