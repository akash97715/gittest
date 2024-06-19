---------------------------------------------------------------------------
ValidationError                           Traceback (most recent call last)
Cell In[11], line 1
----> 1 graph_builder = GraphBuilder(config)
      2 app = graph_builder.compile()

Cell In[10], line 48
     46 self.lambda_wrappers = {}
     47 self._validate_config()
---> 48 self._create_lambda_wrappers()
     49 self._load_config()

Cell In[10], line 72
     70 def _create_lambda_wrappers(self):
     71     for tool in self.config["tools"]:
---> 72         wrapper = LambdaWrapper(
     73             function_name=tool["arn"],
     74             awslambda_tool_name=tool["name"],
     75             awslambda_tool_description=f"Lambda function for {tool['name']}"
     76         )
     77         self.lambda_wrappers[tool["name"]] = wrapper

File c:\Users\akasdeep\Downloads\langgraphmain\agentsenv\Lib\site-packages\pydantic\main.py:176, in BaseModel.__init__(self, **data)
    174 # `__tracebackhide__` tells pytest and some other tools to omit this function from tracebacks
    175 __tracebackhide__ = True
--> 176 self.__pydantic_validator__.validate_python(data, self_instance=self)

ValidationError: 1 validation error for LambdaWrapper
lambda_client
  Field required [type=missing, input_value={'function_name': 'ASFGAG... function for retrieve'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.7/v/missing
