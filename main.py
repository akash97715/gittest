---------------------------------------------------------------------------AttributeError                            Traceback (most recent call last) Cell In[76], line 1----> 1 tool1 = LambdaTool(      2     tool_name="awslambda",      3     region="us-east-1",      4      5     tool_description="Sends an email with specified content",      6     function_name="arn:aws:lambda::function:sbx-vox-agent-tool-example"      7 )      9 tools=[tool1] Cell In[69], line 36, in LambdaTool.__init__(self, function_name, region, tool_name, tool_description, is_conditional, input_schema, output_schema)     25 def __init__(     26     self,      27     function_name: str,    (...)     33     output_schema: Type[BaseModel] = None     34 ):     35     """Initialize the Lambda tool with required parameters."""---> 36     self.lambda_wrapper = LambdaWrapper.create(     37         function_name=function_name,      38 tool_name=tool_name, 39 tool_description=tool_description, 40 region=region,
...
     44     ) File d:\docinsight_langgraph\docinsightlanggraph\Lib\site-packages\pydantic\main.py:405, in pydantic.main.BaseModel.__setattr__()AttributeError: 'LambdaTool' object has no attribute '__fields_set__'
