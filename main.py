import json
from typing import Any, Dict, Optional, Type, Union

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool

# Assuming LambdaWrapper is already defined and available
from your_module.lambda_wrapper import LambdaWrapper  # Adjust import as necessary

class LambdaToolInput(BaseModel):
    """Input schema for the Lambda tool."""
    data: Dict[str, Any] = Field(default_factory=dict, description="Payload to send to the Lambda function.")

class LambdaTool(BaseTool):
    """Tool that interfaces with AWS Lambda to execute functions."""

    name: str = "aws_lambda_execution"
    description: str = "Tool for executing AWS Lambda functions from the langchain framework."
    lambda_wrapper: LambdaWrapper
    args_schema: Type[BaseModel] = LambdaToolInput

    def __init__(
        self, 
        function_name: str, 
        region: str, 
        tool_name: str, 
        tool_description: str, 
        is_conditional: bool = False, 
        input_schema: Type[BaseModel] = None, 
        output_schema: Type[BaseModel] = None
    ):
        """Initialize the Lambda tool with required parameters."""
        self.lambda_wrapper = LambdaWrapper.create(
            function_name=function_name, 
            tool_name=tool_name, 
            tool_description=tool_description, 
            region=region, 
            is_conditional=is_conditional, 
            input_schema=input_schema, 
            output_schema=output_schema
        )

    def _run(
        self, 
        data: Dict[str, Any], 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Union[Dict, str]:
        """Synchronous tool execution."""
        try:
            return self.lambda_wrapper.run(data)
        except Exception as e:
            return str(e)

    async def _arun(
        self, 
        data: Dict[str, Any], 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> Union[Dict, str]:
        """Asynchronous tool execution."""
        try:
            return self.lambda_wrapper.run(data)  # Note: Actual async behavior might require adjustments.
        except Exception as e:
            return str(e)

# Example usage
if __name__ == "__main__":
    lambda_tool = LambdaTool(
        function_name="YourLambdaFunctionName",
        region="us-east-1",
        tool_name="ExampleLambdaTool",
        tool_description="This tool executes a specific AWS Lambda function."
    )
    input_data = LambdaToolInput(data={"key": "value"})
    result = lambda_tool._run(data=input_data.dict())
    print(result)
