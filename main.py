[11:41 PM] Deep, Akash (External)
import json
from typing import Any, Dict, Optional
import boto3
from langchain_core.pydantic_v1 import BaseModel
from api.agent_state import AgentState
 
class LambdaWrapper(BaseModel):
    """Wrapper for AWS Lambda SDK."""
    lambda_client: Any  #: :meta private:
    function_name: Optional[str] = None
    awslambda_tool_name: Optional[str] = None
    awslambda_tool_description: Optional[str] = None
    is_conditional_fn: bool = False
 
    @classmethod
    def create(cls, function_name: str, tool_name: str, tool_description: str, region: str, is_conditional: bool = False):
        lambda_client = boto3.client("lambda", region_name=region)
        return cls(
            lambda_client=lambda_client,
            function_name=function_name,
            awslambda_tool_name=tool_name,
            awslambda_tool_description=tool_description,
            is_conditional_fn=is_conditional
        )
 
    def set_is_conditional(self, is_conditional: bool = False) -> None:
        self.is_conditional_fn = is_conditional
 
    def run(self, state: AgentState) -> str:
        res = self.lambda_client.invoke(
            FunctionName=self.function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps({"body": state}),
        )
        try:
            payload_stream = res["Payload"]
            payload_string = payload_stream.read().decode("utf-8")
            response = json.loads(payload_string)
        except StopIteration:
            return "Failed to parse response from Lambda"
        if response is None or response == "":
            return "Request failed."
        else:
            if self.is_conditional_fn:
                print(f"{self.awslambda_tool_name} returned {response['body']}")
                return str(response["body"])
            updated_payload = state["payload"]
            if updated_payload is not None:
                updated_payload.update(response)
            else:
                updated_payload = response
            return {"messages": [], "payload": updated_payload }
 
 
[11:42 PM] Deep, Akash (External)
 "input_schema": {
      "type": "object",
      "properties": {
        "product_id": {"type": "string"},
        "fields": {
          "type": "array",
          "items": {"type": "string"},
          "description": "List of fields to retrieve (e.g., ['name', 'price', 'description'])"
        }
      },
      "required": ["product_id"]
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "product_id": {"type": "string"},
        "name": {"type": "string"},
        "price": {"type": "number"},
        "description": {"type": "string"},
        "in_stock": {"type": "boolean"}
      },
      "required": ["product_id", "name", "price"]
    }
 
[11:43 PM] Deep, Akash (External)
{
    "name": "Dummy Agent",
    "description": "agent",
    "prompt": "What is the meaning of life?",
    "system_prompt": "Assume that you are a philosopher heavily influenced by Socrates and believe in equilibrium between liberal and capitalist ideas.",
    "tools": [
        { "name": "retriever_tool", "arn": "ASFGAGSDHDSHHDHH-adaHdh", "region": "us-east-1"},
        { "name": "grader_tool", "arn": "ASFGAGSDHDSHHDHH-adaHdh", "region": "us-east-1" },
        { "name": "rewriter_tool", "arn": "ASFGAGSDHDSHHDHH-adaHdh", "region": "us-east-1" },
        { "name": "send_chunks_tool", "arn": "ASFGAGSDHDSHHDHH-adaHdh", "region": "us-east-1" },
        { "name": "how_is_it", "arn": "ASFGAGSDHDSHHDHH-adaHdh", "region": "us-east-1" }
    ],
    "model": "llama3",
    "supported_llms": ["gpt-3.5", "llama3"],
    "entry_point": "retriever_tool",
    "nodes": [
        {
            "name": "retriever_tool",
            "destination": "grader_tool"
        },
        {
            "name": "grader_tool",
            "condition": {
                "deciding_fn": "how_is_it",
                "destination": {
                    "bad": "rewriter_tool",
                    "good": "send_chunks_tool"
                }
            }
        },
        {
            "name": "rewriter_tool",
            "destination": "retriever_tool"
        },
        {
            "name": "send_chunks_tool",
            "destination": "END"
        }
    ]
}
 
