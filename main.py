---------------------------------------------------------------------------AttributeError
                            Traceback (most recent call last)Cell
In[27], line 1----> 1
tool_instance = LambdaTool(      2     function_name="arn:aws:lambda:us-east-1:420737321821:function:sbx-vox-agent-tool-example",      3     region="us-east-1",      4     tool_name="send_email",      5     tool_description="Sends an email with specified content"      6 ) Cell
In[26], line 28
, in LambdaTool.__init__
(self, function_name, region, tool_name, tool_description, is_conditional, input_schema, output_schema)
     25 def __init__(self, function_name: str, region: str, tool_name: str, tool_description: str,     26              is_conditional: bool = False, input_schema: Type[BaseModel] = None,     27              output_schema: Type[BaseModel] = None):
---> 28
     self.name = tool_name     29     self.description = tool_description     30     self.lambda_wrapper = LambdaWrapper.create(     31         function_name=function_name,     32         tool_name=tool_name,
   (...)
     37         output_schema=output_schema     38     ) File
d:\docinsight_langgraph\docinsightlanggraph\Lib\site-packages\pydantic\main.py:405
, in pydantic.main.BaseModel.__setattr__
()
 
AttributeError
: 'LambdaTool' object has no attribute '__fields_set__'
