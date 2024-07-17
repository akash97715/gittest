import json
import boto3
from pydantic import BaseModel, ValidationError, create_model
from typing import Any, Optional, Dict
from botocore.exceptions import ClientError

class LambdaWrapper(BaseModel):
    lambda_client: Any
    function_name: Optional[str] = None
    awslambda_tool_name: Optional[str] = None
    awslambda_tool_description: Optional[str] = None
    is_conditional_fn: bool = False
    dynamo_client = boto3.client('dynamodb', region_name='your-region')  # specify your AWS region

    @classmethod
    def create(cls, function_name: str, tool_name: str, tool_description: str, region: str, is_conditional: bool = False):
        lambda_client = boto3.client('lambda', region_name=region)
        return cls(
            lambda_client=lambda_client,
            function_name=function_name,
            awslambda_tool_name=tool_name,
            awslambda_tool_description=tool_description,
            is_conditional_fn=is_conditional
        )

    def fetch_schema(self, schema_type: str) -> Dict:
        """
        Fetch schema from DynamoDB based on tool name and schema type ('input' or 'output').
        """
        try:
            response = self.dynamo_client.get_item(
                TableName='SchemaTableName',  # replace with your table name
                Key={
                    'tool_name': {'S': self.awslambda_tool_name},
                    'schema_type': {'S': schema_type}  # assuming schema_type is part of the key
                }
            )
            return json.loads(response['Item']['schema']['S'])
        except ClientError as e:
            print(f"Failed to fetch schema: {e}")
            return {}

    def validate_data(self, data: Dict, schema: Dict) -> Dict:
        """
        Validate data using a dynamically generated Pydantic model from the schema.
        """
        fields = {key: (eval(value['type']), ...) for key, value in schema['properties'].items()}
        DynamicModel = create_model('DynamicModel', **fields)
        try:
            DynamicModel(**data)
        except ValidationError as e:
            return {"error": "Validation failed", "details": str(e)}
        return data

    def run(self, state: Dict) -> Dict:
        # Fetch and validate input using the schema
        input_schema = self.fetch_schema('input')
        validated_input = self.validate_data(state, input_schema)
        if 'error' in validated_input:
            return validated_input
        
        # Invoke the Lambda function
        response = self.lambda_client.invoke(
            FunctionName=self.function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps({"body": state})
        )
        payload_string = response['Payload'].read().decode('utf-8')
        output_data = json.loads(payload_string)

        # Fetch and validate output using the schema
        output_schema = self.fetch_schema('output')
        validated_output = self.validate_data(output_data, output_schema)
        if 'error' in validated_output:
            return validated_output

        return output_data




{
    "name": "Sample Workflow",
    "description": "This workflow processes data through three sequential tools",
    "prompt": "Process this sample payload",
    "system_prompt": "Initiating processing chain...",
    "tools": [
        {
            "name": "data_enrichment",
            "arn": "arn:aws:lambda:us-east-1:123456789012:function:dataEnrichmentTool",
            "region": "us-east-1"
        },
        {
            "name": "data_validation",
            "arn": "arn:aws:lambda:us-east-1:123456789012:function:dataValidationTool",
            "region": "us-east-1"
        },
        {
            "name": "data_storage",
            "arn": "arn:aws:lambda:us-east-1:123456789012:function:dataStorageTool",
            "region": "us-east-1"
        }
    ],
    "model": "dynamic_processing",
    "supported_llms": ["aws_lambda"],
    "entry_point": "data_enrichment",
    "nodes": [
        {
            "name": "data_enrichment",
            "destination": "data_validation"
        },
        {
            "name": "data_validation",
            "destination": "data_storage"
        },
        {
            "name": "data_storage",
            "destination": "END"
        }
    ]
}



{
    "id": "123",
    "message": "Hello, process this message through the workflow."
}



def execute_workflow(config, input_json):
    workflow = Workflow(config)
    result = workflow.run(input_json)
    return result

# Assuming the above configuration and input JSON
config = {
    # Insert the JSON configuration here
}
input_json = {
    "id": "123",
    "message": "Hello, process this message through the workflow."
}

# Execute the workflow
output = execute_workflow(config, input_json)
print(output)
