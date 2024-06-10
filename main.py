->
1191
     super().__init__(  
1192
         engine=engine,  
1193
         temperature=temperature,  
1194
         max_tokens=max_tokens,  
1195
         user_query=user_query,  
1196
         min_response_token=min_response_token,  
1197
         system_message=system_message,  
1198
         client_id=client_id,  
1199
         x_vsl_client_id=x_vsl_client_id,  
1200
         bearer_token=bearer_token,  
1201
         context=context,  
1202
     )  
1203
     self.n = n  
1204
     self.streaming = streaming File
d:\agentenv\Lib\site-packages\pydantic\main.py:345
, in pydantic.main.BaseModel.__init__()  TypeError: Model values must be a dict; you may not have returned a dictionary from a root validator
