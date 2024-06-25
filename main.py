import json
import boto3
import pandas as pd
import io
from sqlalchemy import create_engine
import requests

# Initialize clients
s3_client = boto3.client('s3')
rds_client = boto3.client('rds')

# Environment variables
S3_BUCKET = 'your-s3-bucket'
PARQUET_FILE = 'summaries.parquet'
DB_HOST = 'your-rds-host'
DB_USER = 'your-db-user'
DB_PASSWORD = 'your-db-password'
DB_NAME = 'your-db-name'

# Mock function to simulate API call for summarizing a chunk
def summarize_chunk(chunk):
    # Replace this with your actual API endpoint and request payload
    response = requests.post('https://api.example.com/summarize', json={'chunk': chunk})
    return response.json()['summary']

# Function to check if a summary exceeds the token limit
def exceeds_token_limit(summary, max_token_size):
    return len(summary.split()) > max_token_size

# Recursive reduce function to handle max_token issue
def reduce_summaries(summaries, max_token_size):
    while len(summaries) > 1 or exceeds_token_limit(summaries[0], max_token_size):
        reduced_summaries = []
        for i in range(0, len(summaries), max_token_size):
            batch = summaries[i:i + max_token_size]
            combined_summary = summarize_chunk(" ".join(batch))
            reduced_summaries.append(combined_summary)
        summaries = reduced_summaries
    return summaries[0]

# Final map-reduce step to summarize the summaries of the batches
def final_summary(summaries, max_token_size=500):
    return reduce_summaries(summaries, max_token_size)

# Function to load or create the parquet file
def load_or_create_parquet(file_key, create_new):
    try:
        if create_new:
            return pd.DataFrame(columns=['summary'])
        else:
            obj = s3_client.get_object(Bucket=S3_BUCKET, Key=file_key)
            return pd.read_parquet(io.BytesIO(obj['Body'].read()))
    except Exception as e:
        print(f"Error loading parquet file: {e}")
        return pd.DataFrame(columns=['summary'])

# Function to save the parquet file to S3
def save_parquet_to_s3(df, file_key):
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    s3_client.put_object(Bucket=S3_BUCKET, Key=file_key, Body=buffer.getvalue())

# Function to save final summary to RDS
def save_summary_to_rds(document_name, final_summary):
    engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    connection = engine.connect()
    try:
        connection.execute(f"INSERT INTO summaries (document_name, summary) VALUES ('{document_name}', '{final_summary}')")
    finally:
        connection.close()

def lambda_handler(event, context):
    chunks = event['chunks']
    document_name = event['document_name']
    create_new = event['create_new']
    final_call = event.get('final_call', False)

    # Step 1: Process chunks and get summaries
    batch_summaries = [summarize_chunk(chunk) for chunk in chunks]

    # Step 2: Load or create the parquet file
    df = load_or_create_parquet(PARQUET_FILE, create_new)

    # Step 3: Append the new summaries
    new_summaries_df = pd.DataFrame({'summary': batch_summaries})
    df = pd.concat([df, new_summaries_df], ignore_index=True)

    # Step 4: Save the updated parquet file back to S3
    save_parquet_to_s3(df, PARQUET_FILE)

    # Step 5: If this is the final call, compute the final summary and save to RDS
    if final_call:
        final_summary_result = final_summary(df['summary'].tolist())
        save_summary_to_rds(document_name, final_summary_result)

    return {
        'statusCode': 200,
        'body': json.dumps('Process completed successfully')
    }





{
  "StartAt": "ProcessChunks",
  "States": {
    "ProcessChunks": {
      "Type": "Map",
      "ItemsPath": "$.chunks",
      "MaxConcurrency": 10,
      "Iterator": {
        "StartAt": "InvokeLambda",
        "States": {
          "InvokeLambda": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:your-region:your-account-id:function:your-lambda-function-name",
            "End": true
          }
        }
      },
      "ResultPath": "$.results",
      "Next": "FinalSummary"
    },
    "FinalSummary": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:your-region:your-account-id:function:your-lambda-function-name",
      "Parameters": {
        "final_call": true,
        "document_name": "$.document_name"
      },
      "End": true
    }
  }
}




import json
import boto3
import pandas as pd
from sqlalchemy import create_engine
from concurrent.futures import ThreadPoolExecutor

# Initialize clients
s3_client = boto3.client('s3')
rds_client = boto3.client('rds')

# Environment variables
S3_BUCKET = 'your-s3-bucket'
PARQUET_FILE = 'summaries.parquet'
DB_HOST = 'your-rds-host'
DB_USER = 'your-db-user'
DB_PASSWORD = 'your-db-password'
DB_NAME = 'your-db-name'

# Mock function to simulate API call for summarizing a chunk
def summarize_chunk(chunk):
    # Replace this with your actual API endpoint and request payload
    response = requests.post('https://api.example.com/summarize', json={'chunk': chunk})
    return response.json()['summary']

# Process chunks in batches and summarize each batch
def process_batches(chunks, batch_size=100):
    summaries = []
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            # Using map to apply summarize_chunk function to each chunk in the batch
            batch_summaries = list(executor.map(summarize_chunk, batch))
            # Combine summaries of the batch into a single summary
            combined_summary = summarize_chunk(" ".join(batch_summaries))
            summaries.append(combined_summary)
    return summaries

# Function to check if a summary exceeds the token limit
def exceeds_token_limit(summary, max_token_size):
    return len(summary.split()) > max_token_size

# Recursive reduce function to handle max_token issue
def reduce_summaries(summaries, max_token_size):
    while len(summaries) > 1 or exceeds_token_limit(summaries[0], max_token_size):
        reduced_summaries = []
        for i in range(0, len(summaries), max_token_size):
            batch = summaries[i:i + max_token_size]
            combined_summary = summarize_chunk(" ".join(batch))
            reduced_summaries.append(combined_summary)
        summaries = reduced_summaries
    return summaries[0]

# Final map-reduce step to summarize the summaries of the batches
def final_summary(summaries, max_token_size=500):
    return reduce_summaries(summaries, max_token_size)

# Function to load or create the parquet file
def load_or_create_parquet(file_key, create_new):
    try:
        if create_new:
            return pd.DataFrame(columns=['summary'])
        else:
            obj = s3_client.get_object(Bucket=S3_BUCKET, Key=file_key)
            return pd.read_parquet(obj['Body'])
    except Exception as e:
        print(f"Error loading parquet file: {e}")
        return pd.DataFrame(columns=['summary'])

# Function to save the parquet file to S3
def save_parquet_to_s3(df, file_key):
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    s3_client.put_object(Bucket=S3_BUCKET, Key=file_key, Body=buffer.getvalue())

# Function to save final summary to RDS
def save_summary_to_rds(document_name, final_summary):
    engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    connection = engine.connect()
    try:
        connection.execute(f"INSERT INTO summaries (document_name, summary) VALUES ('{document_name}', '{final_summary}')")
    finally:
        connection.close()

def lambda_handler(event, context):
    chunks = event['chunks']
    document_name = event['document_name']
    create_new = event['create_new']

    # Step 1: Process batches and get summaries
    batch_summaries = process_batches(chunks)

    # Step 2: Load or create the parquet file
    df = load_or_create_parquet(PARQUET_FILE, create_new)

    # Step 3: Append the new summaries
    new_summaries_df = pd.DataFrame({'summary': batch_summaries})
    df = pd.concat([df, new_summaries_df], ignore_index=True)

    # Step 4: Save the updated parquet file back to S3
    save_parquet_to_s3(df, PARQUET_FILE)

    # Step 5: If this is the final call, compute the final summary and save to RDS
    if event.get('final_call'):
        final_summary_result = final_summary(df['summary'].tolist())
        save_summary_to_rds(document_name, final_summary_result)

    return {
        'statusCode': 200,
        'body': json.dumps('Process completed successfully')
    }




import requests
from concurrent.futures import ThreadPoolExecutor

# Mock function to simulate API call for summarizing a chunk
def summarize_chunk(chunk):
    # Replace this with your actual API endpoint and request payload
    response = requests.post('https://api.example.com/summarize', json={'chunk': chunk})
    return response.json()['summary']

# Process chunks in batches and summarize each batch
def process_batches(chunks, batch_size=100):
    summaries = []
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            # Using map to apply summarize_chunk function to each chunk in the batch
            batch_summaries = list(executor.map(summarize_chunk, batch))
            # Combine summaries of the batch into a single summary
            combined_summary = summarize_chunk(" ".join(batch_summaries))
            summaries.append(combined_summary)
    return summaries

# Function to check if a summary exceeds the token limit
def exceeds_token_limit(summary, max_token_size):
    return len(summary.split()) > max_token_size

# Recursive reduce function to handle max_token issue
def reduce_summaries(summaries, max_token_size):
    while len(summaries) > 1 or exceeds_token_limit(summaries[0], max_token_size):
        reduced_summaries = []
        for i in range(0, len(summaries), max_token_size):
            batch = summaries[i:i + max_token_size]
            combined_summary = summarize_chunk(" ".join(batch))
            reduced_summaries.append(combined_summary)
        summaries = reduced_summaries
    return summaries[0]

# Final map-reduce step to summarize the summaries of the batches
def final_summary(summaries, max_token_size=500):
    return reduce_summaries(summaries, max_token_size)

# Example usage
if __name__ == "__main__":
    # Mock chunks data
    chunks = ["chunk" + str(i) for i in range(1000)]

    # Step 1: Process batches and get summaries
    batch_summaries = process_batches(chunks)

    # Step 2: Apply map-reduce technique to get final summary
    final_summary_result = final_summary(batch_summaries)

    print("Final Summary:", final_summary_result)
