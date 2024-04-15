import boto3
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

class Document:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

s3 = boto3.client('s3')
bucket_name = 'your-bucket-name'

def parse_content(key):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except json.JSONDecodeError:
        return {'content': content}

def fetch_document(key):
    return Document(**parse_content(key))

keys = ['your-key-1', 'your-key-2', ..., 'your-key-673']  # List of keys

# Using ThreadPoolExecutor to fetch and process documents in parallel
with ThreadPoolExecutor(max_workers=20) as executor:
    future_to_key = {executor.submit(fetch_document, key): key for key in keys}
    documents = []
    for future in as_completed(future_to_key):
        try:
            document = future.result()
            documents.append(document)
        except Exception as exc:
            print(f'Key {future_to_key[future]} generated an exception: {exc}')

# documents now contains all your Document instances
