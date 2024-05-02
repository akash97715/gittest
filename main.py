import json
import requests

def lambda_handler(event, context):
    response = requests.get("https://api.example.com/data")
    return {
        'statusCode': 200,
        'body': json.dumps(response.json())
    }


cd lambda-env\Lib\site-packages


Compress-Archive -Path * -DestinationPath C:\path\to\your\project\function.zip -Force


cd C:\path\to\your\project


Compress-Archive -Path lambda_function.py -Update -DestinationPath function.zip
