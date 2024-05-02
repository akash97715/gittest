from fastapi import FastAPI
from typing import List
import httpx
import boto3
import asyncio

app = FastAPI()

# Initialize the Lambda client
lambda_client = boto3.client('lambda', region_name='your-region')

async def invoke_lambda_async(payload):
    """
    Asynchronously invoke the AWS Lambda function.
    """
    # Convert payload to JSON if it's not a string (depends on your data)
    if not isinstance(payload, str):
        payload = json.dumps(payload)

    response = await asyncio.to_thread(
        lambda_client.invoke,
        FunctionName='your-lambda-function-name',
        InvocationType='RequestResponse',
        Payload=payload
    )
    return response['Payload'].read()

@app.post("/invoke-lambdas/")
async def invoke_lambdas(data: List):
    """
    Endpoint to invoke Lambda function in parallel for each item in the list.
    """
    # Create tasks for each item in the list
    tasks = [invoke_lambda_async(item) for item in data]
    
    # Run tasks concurrently and wait for all to complete
    results = await asyncio.gather(*tasks)
    
    return {"results": results, "status": "Completed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
