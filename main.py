--------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Cell In[18], line 1
----> 1 graph_builder = GraphBuilder(config)
      2 app = graph_builder.compile()

Cell In[8], line 47
     45 self.workflow = StateGraph(GraphState)
     46 self.lambda_wrappers = {}
---> 47 self._validate_config()
     48 self._create_lambda_wrappers()
     49 self._load_config()

Cell In[8], line 68
     63 end_state_found = any(
     64     value == END for node in self.config["nodes"]
     65     for value in node.get("condition", {}).get("process", {}).values()
     66 )
     67 if not end_state_found:
---> 68     raise ValueError("No end state specified in any of the conditional edges.")

ValueError: No end state specified in any of the conditional edges.
