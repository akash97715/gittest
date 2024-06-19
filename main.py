---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
Cell In[28], line 1
----> 1 graph_builder = GraphBuilder(config)
      2 app = graph_builder.compile()

Cell In[26], line 9
      7 self.workflow = StateGraph(GraphState)
      8 self._validate_config()
----> 9 self._load_config()

Cell In[26], line 30
     27 nodes = {node["name"]: node for node in self.config["nodes"]}
     29 for node in self.config["nodes"]:
---> 30     self.workflow.add_node(node["name"], None)  # Replace None with actual function references
     32 self.workflow.set_entry_point(self.config["entry_point"])
     34 for node in self.config["nodes"]:

File c:\Users\akasdeep\Downloads\langgraphmain\agentsenv\Lib\site-packages\langgraph\graph\state.py:168, in StateGraph.add_node(self, node, action)
    166 if node in self.channels:
    167     raise ValueError(f"'{node}' is already being used as a state key")
--> 168 return super().add_node(node, action)

File c:\Users\akasdeep\Downloads\langgraphmain\agentsenv\Lib\site-packages\langgraph\graph\graph.py:151, in Graph.add_node(self, node, action)
    148 if node == END or node == START:
    149     raise ValueError(f"Node `{node}` is reserved.")
--> 151 self.nodes[node] = coerce_to_runnable(action, name=node, trace=False)

File c:\Users\akasdeep\Downloads\langgraphmain\agentsenv\Lib\site-packages\langgraph\utils.py:206, in coerce_to_runnable(thing, name, trace)
    204     return RunnableParallel(thing)
    205 else:
--> 206     raise TypeError(
    207         f"Expected a Runnable, callable or dict."
    208         f"Instead got an unsupported type: {type(thing)}"
    209     )

TypeError: Expected a Runnable, callable or dict.Instead got an unsupported type: <class 'NoneType'>
