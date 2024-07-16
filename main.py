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



from langgraph.graph import StateGraph, END
from typing import Sequence, TypedDict, Annotated
# from langchain_community.chat_models import ChatOllama, ChatOpenAI
from pydantic import Field
from collections import deque
import json
from api.lambda_tools_wrapper import LambdaWrapper
from api.agent_state import AgentState
 
def runnable_action(tool_name):
    return tool_name
 
 
class Workflow:
    def __init__(self, config):
        self.config = config
        self.workflow = StateGraph(AgentState)
        self.lambda_wrappers : dict[LambdaWrapper] = {}
        self._validate_config()
        self._create_lambda_wrappers()
        self._load_config()
 
    def _validate_config(self):
        required_keys = ["name", "description", "prompt", "system_prompt", "tools", "model", "entry_point", "nodes"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
       
        # if not any(node.get('condition') for node in self.config["nodes"]):
        #     raise ValueError("No conditional edges defined in the nodes.")
       
        if self.config.get("entry_point") not in [node["name"] for node in self.config["nodes"]]:
            raise ValueError("Invalid entry point specified.")
 
        end_state_found = any(
            value == "END" for node in self.config["nodes"]
            for value in (node.get("condition").get("destination").values() if node.get("condition") is not None
            else [node.get("destination")])
        )
        if not end_state_found:
            raise ValueError("No end state specified in any of the conditional edges.")
 
    def _create_lambda_wrappers(self):
        for tool in self.config["tools"]:
            wrapper = LambdaWrapper.create(
                function_name=tool["arn"],
                tool_name=tool["name"],
                tool_description=f"Lambda function for {tool['name']}",
                region=tool["region"]
            )
            self.lambda_wrappers[tool["name"]] = wrapper
 
    def _load_config(self):
        for node in self.config["nodes"]:
            action = self.lambda_wrappers.get(node["name"])
            self.workflow.add_node(node["name"], action.run)
 
        self.workflow.set_entry_point(self.config["entry_point"])
 
        for node in self.config["nodes"]:
            if "condition" in node:
                condition = node["condition"]
                deciding_fn: LambdaWrapper = self.lambda_wrappers.get(condition["deciding_fn"])
                self.workflow.add_conditional_edges(
                    node["name"],
                    deciding_fn.run,
                    {key: (value if value != "END" else END) for key, value in condition["destination"].items()}
                )
                deciding_fn.set_is_conditional(True)
            elif "destination" in node:
                self.workflow.add_edge(node["name"], node["destination"] if node["destination"] != "END" else END)
            else:
                raise ValueError("No destination found for the node!")
 
    def compile(self):
        app = self.workflow.compile()
        try:
            print("Workflow compiled")
            # graph.get_graph(xray=True).draw_png("./app/example/graph.png")
        except Exception:
            print(Exception)
        return app
 
