from typing import Any, Dict, Optional, Type, Union
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

class LambdaTool(BaseTool):
    """Tool that interfaces with AWS Lambda to execute functions."""
    name: str = Field(default="aws_lambda_execution", description="Name of the tool")
    description: str = Field(
        default="Tool for executing AWS Lambda functions from the langchain framework.",
        description="Description of the tool"
    )
    lambda_wrapper: LambdaWrapper = Field(..., description="Wrapper for the AWS Lambda client")
    args_schema: Type[BaseModel] = Field(default=LambdaInput, description="Input schema for the lambda tool")

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def create(cls, function_name: str, region: str, tool_name: str, tool_description: str,
               is_conditional: bool = False, input_schema: Type[BaseModel] = None, 
               output_schema: Type[BaseModel] = None) -> "LambdaTool":
        """Factory method to create a new instance of LambdaTool."""
        lambda_wrapper = LambdaWrapper.create(
            function_name=function_name,
            tool_name=tool_name,
            tool_description=tool_description,
            region=region,
            is_conditional=is_conditional,
            input_schema=input_schema,
            output_schema=output_schema
        )
        return cls(lambda_wrapper=lambda_wrapper)

    def _run(self, data: Dict[str, Any], run_manager: Optional[CallbackManagerForToolRun] = None) -> Union[Dict, str]:
        """Synchronous tool execution."""
        return self.lambda_wrapper.run(data)

    async def _arun(self, data: Dict[str, Any], run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> Union[Dict, str]:
        """Asynchronous tool execution."""
        return await self._run(data, run_manager)
