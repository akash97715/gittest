import boto3
import json
from typing import Any, Dict, Optional
from langgraph.graph import END, StateGraph
from IPython.display import Image, display
from pydantic import BaseModel, root_validator

class LambdaWrapper(BaseModel):
    """Wrapper for AWS Lambda SDK."""
    lambda_client: Any  #: :meta private:
    function_name: Optional[str] = None
    awslambda_tool_name: Optional[str] = None
    awslambda_tool_description: Optional[str] = None

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        try:
            import boto3
        except ImportError:
            raise ImportError(
                "boto3 is not installed. Please install it with `pip install boto3`"
            )
        values["lambda_client"] = boto3.client("lambda")
        values["function_name"] = values["function_name"]
        return values

    def run(self, query: str) -> str:
        res = self.lambda_client.invoke(
            FunctionName=self.function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps({"body": query}),
        )
        try:
            payload_stream = res["Payload"]
            payload_string = payload_stream.read().decode("utf-8")
            answer = json.loads(payload_string)["body"]
        except StopIteration:
            return "Failed to parse response from Lambda"
        if answer is None or answer == "":
            return "Request failed."
        else:
            return f"Result: {answer}"

class GraphBuilder:
    def __init__(self, config):
        self.config = config
        self.workflow = StateGraph(GraphState)
        self.lambda_wrappers = {}
        self._validate_config()
        self._create_lambda_wrappers()
        self._load_config()

    def _validate_config(self):
        required_keys = ["name", "type", "prompt", "system_prompt", "tools", "model", "entry_point", "nodes"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
        
        if not any(node.get('condition') for node in self.config["nodes"]):
            raise ValueError("No conditional edges defined in the nodes.")
        
        if self.config.get("entry_point") not in [node["name"] for node in self.config["nodes"]]:
            raise ValueError("Invalid entry point specified.")

        end_state_found = any(
            value == "END" for node in self.config["nodes"]
            for value in node.get("condition", {}).get("process", {}).values()
        )
        if not end_state_found:
            raise ValueError("No end state specified in any of the conditional edges.")

    def _create_lambda_wrappers(self):
        for tool in self.config["tools"]:
            wrapper = LambdaWrapper(
                function_name=tool["arn"],
                awslambda_tool_name=tool["name"],
                awslambda_tool_description=f"Lambda function for {tool['name']}"
            )
            self.lambda_wrappers[tool["name"]] = wrapper

    def _load_config(self):
        for node in self.config["nodes"]:
            action = self.lambda_wrappers.get(node["name"], None)
            self.workflow.add_node(node["name"], action.run)

        self.workflow.set_entry_point(self.config["entry_point"])

        for node in self.config["nodes"]:
            if "destination" in node:
                self.workflow.add_edge(node["name"], node["destination"])

            if "condition" in node:
                condition = node["condition"]
                deciding_fn = self.lambda_wrappers.get(condition["deciding_fn"], None)
                self.workflow.add_conditional_edges(
                    node["name"],
                    deciding_fn.run,
                    {key: (value if value != "END" else END) for key, value in condition["process"].items()}
                )

    def compile(self):
        app = self.workflow.compile()
        try:
            display(Image(app.get_graph(xray=True).draw_mermaid_png()))
        except Exception:
            print(Exception)
            pass
        return app

# Example usage
config = {
    "name": "Dummy Agent",
    "type": "agent",
    "prompt": "What is the meaning of life?",
    "system_prompt": "Assume that you are a philosopher heavily influenced by Socrates and believe in equilibrium between liberal and capitalist ideas.",
    "tools": [
        { "name": "retrieve", "method": "GET", "arn": "arn:aws:lambda:region:account-id:function:retrieve" },
        { "name": "grade_documents", "method": "POST", "arn": "arn:aws:lambda:region:account-id:function:grade_documents" },
        { "name": "generate", "method": "PUT", "arn": "arn:aws:lambda:region:account-id:function:generate" },
        { "name": "transform_query", "method": "GET", "arn": "arn:aws:lambda:region:account-id:function:transform_query" },
        { "name": "decide_to_generate", "method": "GET", "arn": "arn:aws:lambda:region:account-id:function:decide_to_generate" },
        { "name": "grade_generation_v_documents_and_question", "method": "GET", "arn": "arn:aws:lambda:region:account-id:function:grade_generation_v_documents_and_question" }
    ],
    "model": "llama3",
    "entry_point": "retrieve",
    "nodes": [
        {
            "name": "retrieve",
            "destination": "grade_documents"
        },
        {
            "name": "grade_documents",
            "condition": {
                "deciding_fn": "decide_to_generate",
                "process": {
                    "transform_query": "transform_query",
                    "generate": "generate"
                }
            }
        },
        {
            "name": "transform_query",
            "destination": "retrieve"
        },
        {
            "name": "generate",
            "condition": {
                "deciding_fn": "grade_generation_v_documents_and_question",
                "process": {
                    "not supported": "generate",
                    "useful": "END",
                    "not useful": "transform_query"
                }
            }
        }
    ]
}

graph_builder = GraphBuilder(config)
app = graph_builder.compile()
