import boto3

# Initialize a session using your credential and region
session = boto3.Session(
    aws_access_key_id='YOUR_KEY',
    aws_secret_access_key='YOUR_SECRET',
    region_name='YOUR_REGION'
)

# Create an S3 client
s3 = session.client('s3')

# Name of the S3 bucket
bucket_name = 'your-bucket-name'

# List objects within the S3 bucket
def list_objects(bucket_name):
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            print(obj['Key'])

# Call the function
list_objects(bucket_name)
