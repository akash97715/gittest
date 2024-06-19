from langgraph.graph import END, StateGraph
from IPython.display import Image, display

# Dummy functions for demonstration; replace these with actual implementations
def retrieve():
    pass

def grade_documents():
    pass

def generate():
    pass

def transform_query():
    pass

def decide_to_generate():
    pass

def grade_generation_v_documents_and_question():
    pass

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

        if not any("END" in process for node in self.config["nodes"] for process in node.get("condition", {}).get("process", {}).values()):
            raise ValueError("No end state specified in any of the conditional edges.")

    def _load_config(self):
        # Map node names to functions for demonstration purposes
        node_actions = {
            "retrieve": retrieve,
            "grade_documents": grade_documents,
            "generate": generate,
            "transform_query": transform_query,
            "decide_to_generate": decide_to_generate,
            "grade_generation_v_documents_and_question": grade_generation_v_documents_and_question
        }

        for node in self.config["nodes"]:
            action = node_actions.get(node["name"], None)
            self.workflow.add_node(node["name"], action)

        self.workflow.set_entry_point(self.config["entry_point"])

        for node in self.config["nodes"]:
            if "destination" in node:
                self.workflow.add_edge(node["name"], node["destination"])

            if "condition" in node:
                condition = node["condition"]
                deciding_fn = node_actions.get(condition["deciding_fn"], None)
                self.workflow.add_conditional_edges(
                    node["name"],
                    deciding_fn,
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

# Example usage
config = {
    "name": "Dummy Agent",
    "type": "agent",
    "prompt": "What is the meaning of life?",
    "system_prompt": "Assume that you are a philosopher heavily influenced by Socrates and believe in equilibrium between liberal and capitalist ideas.",
    "tools": [
        { "name": "tool1", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "tool2", "method": "POST", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "tool3", "method": "PUT", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "tool4", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "tool5", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "rewrite", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" }
    ],
    "model": "llama3",
    "entry_point": "tool1",
    "nodes": [
        {
            "name": "tool1",
            "destination": "tool2"
        },
        {
            "name": "tool2",
            "destination": "tool3"
        },
        {
            "name": "tool3",
            "condition": {
                "deciding_fn": "rewrite",
                "process": {
                    "tool4": "tool4",
                    "END": "END"
                }
            }
        },
        {
            "name": "tool4",
            "destination": "tool1"
        }
    ]
}

graph_builder = GraphBuilder(config)
app = graph_builder.compile()
