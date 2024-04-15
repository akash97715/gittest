import boto3
import json

class Document:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

# Assuming the initialization of S3 client and bucket name are set up elsewhere
s3 = boto3.client('s3')
bucket_name = 'your-bucket-name'

documents = [Document(**(json.loads(obj["Body"].read().decode('utf-8')) if isinstance(obj["Body"].read().decode('utf-8'), str) else {'content': obj["Body"].read().decode('utf-8')})) for key in keys for obj in [s3.get_object(Bucket=bucket_name, Key=key)]]
