from langgraph.graph import StateGraph, END
from api.lambda_tools_wrapper import LambdaWrapper
from api.agent_state import AgentState
from typing import Dict

class Workflow:
    def __init__(self, config):
        self.config = config
        self.workflow = StateGraph(AgentState)
        self.lambda_wrappers: Dict[str, LambdaWrapper] = {}
        self._validate_config()
        self._create_lambda_wrappers()
        self._load_config()

    def _validate_config(self):
        required_keys = ["name", "description", "prompt", "system_prompt", "tools", "model", "entry_point", "nodes"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")

        if self.config.get("entry_point") not in [node["name"] for node in self.config["nodes"]]:
            raise ValueError("Invalid entry point specified.")

    def _create_lambda_wrappers(self):
        for tool in self.config["tools"]:
            input_schema = tool.get("input_schema")
            output_schema = tool.get("output_schema")
            wrapper = LambdaWrapper.create(
                function_name=tool["arn"],
                tool_name=tool["name"],
                tool_description=f"Lambda function for {tool['name']}",
                region=tool["region"],
                input_schema=input_schema,
                output_schema=output_schema
            )
            self.lambda_wrappers[tool["name"]] = wrapper

    def _load_config(self):
        for node in self.config["nodes"]:
            action = self.lambda_wrappers.get(node["name"])
            if action is None:
                raise ValueError(f"No LambdaWrapper found for {node['name']}. Check tool configuration.")
            self.workflow.add_node(node["name"], action.run)
        self.workflow.set_entry_point(self.config["entry_point"])

        for node in self.config["nodes"]:
            if "condition" in node:
                condition = node["condition"]
                deciding_fn = self.lambda_wrappers.get(condition["deciding_fn"])
                self.workflow.add_conditional_edges(
                    node["name"],
                    deciding_fn.run,
                    {key: (value if value != "END" else END) for key, value in condition["destination"].items()}
                )
                deciding_fn.set_is_conditional(True)
            elif "destination" in node:
                self.workflow.add_edge(node["name"], node["destination"] if node["destination"] != "END" else END)

    def compile(self):
        return self.workflow.compile()
