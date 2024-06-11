class DynamicWorkflow:
    def __init__(self, state_class):
        self.workflow = StateGraph(state_class)
        self.nodes = {}
        self.entry_point = None

    def add_node(self, name, node):
        self.workflow.add_node(name, node)
        self.nodes[name] = node

    def set_entry_point(self, entry_point):
        self.entry_point = entry_point
        self.workflow.set_entry_point(entry_point)

    def add_edge(self, from_node, to_node):
        self.workflow.add_edge(from_node, to_node)

    def add_conditional_edges(self, from_node, condition, condition_map):
        self.workflow.add_conditional_edges(from_node, condition, condition_map)

    def compile(self):
        return self.workflow.compile()


# Example usage:
def tools_condition():
    # Define the condition logic
    pass

# Instantiate the dynamic workflow class
dynamic_workflow = DynamicWorkflow(AgentState)

# Define nodes
dynamic_workflow.add_node("agent", agent)
retrieve = ToolNode([retriever_tool])
dynamic_workflow.add_node("retrieve", retrieve)
dynamic_workflow.add_node("rewrite", rewrite)
dynamic_workflow.add_node("generate", generate)
dynamic_workflow.add_node("grade", grade_documents)

# Set entry point
dynamic_workflow.set_entry_point("agent")

# Add conditional edges
dynamic_workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "retrieve",
        "END": "grade",
    },
)

# Add regular edges
dynamic_workflow.add_edge("retrieve", "grade")
dynamic_workflow.add_edge("generate", "END")
dynamic_workflow.add_edge("rewrite", "agent")
dynamic_workflow.add_edge("grade", "END")

# Compile the workflow
graph = dynamic_workflow.compile()
