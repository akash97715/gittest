import boto3
import json

class Document:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

s3 = boto3.client('s3')
bucket_name = 'your-bucket-name'

def parse_content(key):
    try:
        # Fetch the object from S3
        response = s3.get_object(Bucket=bucket_name, Key=key)
        # Read the content of the object only once and decode
        content = response['Body'].read().decode('utf-8')
        # Try to parse the content as JSON
        return json.loads(content)
    except json.JSONDecodeError:
        # If JSON decoding fails, return as plain string in a dict
        return {'content': content}

# List comprehension to process each key
keys = ['your-key-1', 'your-key-2']  # Example keys
documents = [Document(**parse_content(key)) for key in keys]
