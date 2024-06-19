---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[37], line 1
----> 1 graph_builder = GraphBuilder(config)
      2 app = graph_builder.compile()

Cell In[35], line 27
     25 self.config = config
     26 self.workflow = StateGraph(GraphState)
---> 27 self._validate_config()
     28 self._load_config()

Cell In[35], line 42
     39 if self.config.get("entry_point") not in [node["name"] for node in self.config["nodes"]]:
     40     raise ValueError("Invalid entry point specified.")
---> 42 end_state_found = any(
     43     "END" in process.values() for node in self.config["nodes"] for process in node.get("condition", {}).get("process", {}).items()
     44 )
     45 if not end_state_found:
     46     raise ValueError("No end state specified in any of the conditional edges.")

Cell In[35], line 43
     39 if self.config.get("entry_point") not in [node["name"] for node in self.config["nodes"]]:
     40     raise ValueError("Invalid entry point specified.")
     42 end_state_found = any(
---> 43     "END" in process.values() for node in self.config["nodes"] for process in node.get("condition", {}).get("process", {}).items()
     44 )
     45 if not end_state_found:
     46     raise ValueError("No end state specified in any of the conditional edges.")

AttributeError: 'tuple' object has no attribute 'values'
