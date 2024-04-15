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
        # Read the content of the object and attempt to parse as JSON
        return json.loads(response['Body'].read().decode('utf-8'))
    except json.JSONDecodeError:
        # If JSON decoding fails, return as plain string in a dict
        return {'content': response['Body'].read().decode('utf-8')}

# List comprehension to process each key
documents = [Document(**parse_content(key)) for key in keys]
