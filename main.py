import json
from typing import Any, Optional
import boto3
from langchain_core.pydantic_v1 import BaseModel, ValidationError
from pydantic import validate_arguments
from api.agent_state import AgentState
 
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
        lambda_client = boto3.client("lambda", region_name=region)
        return cls(
            lambda_client=lambda_client,
            function_name=function_name,
            awslambda_tool_name=tool_name,
            awslambda_tool_description=tool_description,
            input_schema=input_schema,
            output_schema=output_schema,
            is_conditional_fn=is_conditional
        )
 
    def set_is_conditional(self, is_conditional: bool = False) -> None:
        self.is_conditional_fn = is_conditional
 
    @validate_arguments
    def validate_input(self, input_data: Dict):
        try:
            self.input_schema(**input_data)
        except ValidationError as e:
            return str(e)
        return None
 
    @validate_arguments
    def validate_output(self, output_data: Dict):
        try:
            self.output_schema(**output_data)
        except ValidationError as e:
            return str(e)
        return None
 
    def run(self, state: AgentState) -> str:
        validation_error = self.validate_input(state)
        if validation_error:
            return {"error": validation_error, "status": "input validation failed"}
        
        res = self.lambda_client.invoke(
            FunctionName=self.function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps({"body": state}),
        )
        payload_stream = res["Payload"]
        payload_string = payload_stream.read().decode("utf-8")
        response = json.loads(payload_string)

        validation_error = self.validate_output(response)
        if validation_error:
            return {"error": validation_error, "status": "output validation failed"}
        
        if self.is_conditional_fn:
            print(f"{self.awslambda_tool_name} returned {response['body']}")
            return str(response["body"])
        updated_payload = state["payload"]
        if updated_payload is not None:
            updated_payload.update(response)
        else:
            updated_payload = response
        return {"messages": [], "payload": updated_payload}
