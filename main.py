import asyncio
import aioboto3
import json

class Document:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

bucket_name = 'your-bucket-name'  # Replace with your actual bucket name

async def parse_content(s3, key):
    try:
        response = await s3.get_object(Bucket=bucket_name, Key=key)
        async with response['Body'] as stream:
            content = await stream.read()
        return json.loads(content.decode('utf-8'))
    except json.JSONDecodeError:
        return {'content': content.decode('utf-8')}

async def fetch_document(s3, key):
    return Document(**await parse_content(s3, key))

async def main():
    session = aioboto3.Session()
    async with session.client('s3', region_name='your-region') as s3:  # specify your region
        keys = ['your-key-1', 'your-key-2', 'your-key-673']  # Replace with your actual keys
        tasks = [fetch_document(s3, key) for key in keys]
        documents = await asyncio.gather(*tasks)
    return documents

# You need to use asyncio.run(main()) to execute main() and get the results.
# However, directly calling asyncio.run in Jupyter can cause problems with the running event loop.
# Hence, we use nest_asyncio to allow nested use of asyncio.run
import nest_asyncio
nest_asyncio.apply()

# Now you can run the main coroutine and retrieve the documents
documents = await main()
