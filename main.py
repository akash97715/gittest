from typing import Any, Dict, Optional, Type, Union
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool

class LambdaTool(BaseTool):
    """Tool that interfaces with AWS Lambda to execute functions."""
    name: str = Field(default="send_email", description="Name of the tool")
    description: str = Field(
        default="Sends an email with specified content. whenever query talks about email forcefully use this tool",
        description="Sends an email with specified content. whenever query talks about email forcefully use this tool"
    )
    lambda_wrapper: Optional[LambdaWrapper] = Field(None, description="Wrapper for the AWS Lambda client")
    args_schema: Type[BaseModel] = LambdaInput

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, function_name: str, region: str, tool_name: str, tool_description: str,
                 is_conditional: bool = False, input_schema: Type[BaseModel] = None,
                 output_schema: Type[BaseModel] = None):
        self.name = tool_name
        self.description = tool_description
        self.lambda_wrapper = LambdaWrapper.create(
            function_name=function_name,
            tool_name=tool_name,
            tool_description=tool_description,
            region=region,
            is_conditional=is_conditional,
            input_schema=input_schema,
            output_schema=output_schema
        )

    @classmethod
    def create(cls, function_name: str, region: str, tool_name: str, tool_description: str,
               is_conditional: bool = False, input_schema: Type[BaseModel] = None,
               output_schema: Type[BaseModel] = None) -> "LambdaTool":
        """Factory method to create a new instance of LambdaTool."""
        return cls(
            function_name=function_name,
            region=region,
            tool_name=tool_name,
            tool_description=tool_description,
            is_conditional=is_conditional,
            input_schema=input_schema,
            output_schema=output_schema
        )

    def _run(self, query, run_manager: Optional[CallbackManagerForToolRun] = None) -> Union[Dict, str]:
        """Synchronous tool execution."""
        if self.lambda_wrapper:
            return self.lambda_wrapper.run(query)
        else:
            raise ValueError("LambdaTool is not initialized with a lambda_wrapper")

    async def _arun(self, data: Dict[str, Any], run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> Union[Dict, str]:
        """Asynchronous tool execution."""
        return await self._run(data, run_manager)

# Create an instance and initialize it simultaneously
tool_instance = LambdaTool(
    function_name="arn:aws:lambda:us-east-1:420737321821:function:sbx-vox-agent-tool-example",
    region="us-east-1",
    tool_name="send_email",
    tool_description="Sends an email with specified content"
)
