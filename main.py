from langgraph.graph import END, StateGraph
from IPython.display import Image, display

class GraphBuilder:
    def __init__(self, config):
        self.config = config
        self.workflow = StateGraph(GraphState)
        self._validate_config()
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

        if not any("END" in node.get("condition", {}).get("process", "") for node in self.config["nodes"]):
            raise ValueError("No end state specified in the conditional edges.")

    def _load_config(self):
        nodes = {node["name"]: node for node in self.config["nodes"]}

        for node in self.config["nodes"]:
            self.workflow.add_node(node["name"], None)  # Replace None with actual function references

        self.workflow.set_entry_point(self.config["entry_point"])

        for node in self.config["nodes"]:
            if "destination" in node:
                self.workflow.add_edge(node["name"], node["destination"])

            if "condition" in node:
                condition = node["condition"]
                self.workflow.add_conditional_edges(
                    node["name"],
                    condition["deciding_fn"],  # Replace with actual function references
                    {key: value for key, value in condition["process"].items()}
                )

    def compile(self):
        app = self.workflow.compile()
        try:
            display(Image(app.get_graph(xray=True).draw_mermaid_png()))
        except Exception:
            print(Exception)
            pass
        return app
