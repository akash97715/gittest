import json
import boto3
from langchain_core.pydantic_v1 import BaseModel, ValidationError
from pydantic import validate_call
from typing import Any, Optional, Dict

class LambdaWrapper(BaseModel):
    lambda_client: Any
    function_name: Optional[str] = None
    awslambda_tool_name: Optional[str] = None
    awslambda_tool_description: Optional[str] = None
    is_conditional_fn: bool = False
    input_schema: BaseModel = None
    output_schema: BaseModel = None
 
    @classmethod
    def create(cls, function_name: str, tool_name: str, tool_description: str, region: str, input_schema: BaseModel, output_schema: BaseModel, is_conditional: bool = False):
        lambda_client = boto3.client('lambda', region_name=region)
        return cls(
            lambda_client=lambda_client,
            function_name=function_name,
            awslambda_tool_name=tool_name,
            awslambda_tool_description=tool_description,
            input_schema=input_schema,
            output_schema=output_schema,
            is_conditional_fn=is_conditional
        )
 
    @validate_call
    def validate_input(self, input_data: Dict):
        if self.input_schema:
            self.input_schema(**input_data)

    @validate_call
    def validate_output(self, output_data: Dict):
        if self.output_schema:
            self.output_schema(**output_data)

    def run(self, state: Dict) -> Dict:
        self.validate_input(state)
        response = self.lambda_client.invoke(
            FunctionName=self.function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps({"body": state})
        )
        payload_string = response['Payload'].read().decode('utf-8')
        output_data = json.loads(payload_string)
        self.validate_output(output_data)
        return output_data
