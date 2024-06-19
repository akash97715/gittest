Cell In[29], line 76
     75 def compile(self):
---> 76     app = self.workflow.compile()
     77     try:
     78         display(Image(app.get_graph(xray=True).draw_mermaid_png()))

File c:\Users\akasdeep\Downloads\langgraphmain\agentsenv\Lib\site-packages\langgraph\graph\state.py:233, in StateGraph.compile(self, checkpointer, interrupt_before, interrupt_after, debug)
    230 interrupt_after = interrupt_after or []
    232 # validate the graph
--> 233 self.validate(
    234     interrupt=(
    235         (interrupt_before if interrupt_before != "*" else []) + interrupt_after
    236         if interrupt_after != "*"
    237         else []
    238     )
    239 )
    241 # prepare output channels
    242 state_keys = list(self.channels)

File c:\Users\akasdeep\Downloads\langgraphmain\agentsenv\Lib\site-packages\langgraph\graph\graph.py:303, in Graph.validate(self, interrupt)
    301     for end in branch.ends.values():
    302         if end not in self.nodes and end != END:
--> 303             raise ValueError(
    304                 f"At '{start}' node, '{cond}' branch found unknown target '{end}'"
    305             )
    306         all_targets.add(end)
    307 else:

ValueError: At 'generate' node, 'grade_generation_v_documents_and_question' branch found unknown target 'END'

config = {
    "name": "Dummy Agent",
    "type": "agent",
    "prompt": "What is the meaning of life?",
    "system_prompt": "Assume that you are a philosopher heavily influenced by Socrates and believe in equilibrium between liberal and capitalist ideas.",
    "tools": [
        { "name": "retrieve", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "grade_documents", "method": "POST", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "generate", "method": "PUT", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "transform_query", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "decide_to_generate", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" },
        { "name": "grade_generation_v_documents_and_question", "method": "GET", "arn": "ASFGAGSDHDSHHDHH-adaHdh" }
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
