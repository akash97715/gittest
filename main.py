[12:21 PM] Deep, Akash (External)
# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.invoke({"input": "what is LangChain?"})
 
[12:22 PM] Deep, Akash (External)
Entering new AgentExecutor chain... LangChain is a framework for building and deploying decentralized applications.Action: aws_lambda_executionAction Input: N/A
Output exceeds the size limit. Open the full output data in a text editor
---------------------------------------------------------------------------ValidationError                           Traceback (most recent call last) Cell In[83], line 1----> 1 agent_executor.invoke({"input": "what is LangChain?"}) File d:\docinsight_langgraph\docinsightlanggraph\Lib\site-packages\langchain\chains\base.py:166, in Chain.invoke(self, input, config, **kwargs)    164 except BaseException as e:    165     run_manager.on_chain_error(e)--> 166     raise e    167 run_manager.on_chain_end(outputs)    169 if include_run_info: File d:\docinsight_langgraph\docinsightlanggraph\Lib\site-packages\langchain\chains\base.py:156, in Chain.invoke(self, input, config, **kwargs)    153 try:    154     self._validate_inputs(inputs)    155     outputs = (--> 156         self._call(inputs, run_manager=run_manager)    157         if new_arg_supported    158         else self._call(inputs)    159     )    161     final_outputs: Dict[str, Any] = self.prep_outputs(    162         inputs, outputs, return_only_outputs    163     )    164 except BaseException as e:
...
File d:\docinsight_langgraph\docinsightlanggraph\Lib\site-packages\pydantic\main.py:341, in pydantic.main.BaseModel.__init__()ValidationError: 1 validation error for LambdaToolInput data   value is not a valid dict (type=type_error.dict)
 
