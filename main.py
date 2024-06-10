---------------------------------------------------------------------------AttributeError                            Traceback (most recent call last)Cell In[11],
line 8
     
1
import pprint     
3
inputs = {     
4
     "messages": [     
5
         ("user", "What does Lilian Weng say about the types of agent memory?"),     
6
     ]     
7
}---->
8
for output in graph.stream(inputs):     
9
     for key, value in output.items():    
10
         pprint.pprint(f"Output from node '{key}':") File
d:\agentenv\Lib\site-packages\langgraph\pregel\__init__.py:963
, in Pregel.stream(self, input, config, stream_mode, output_keys, input_keys, interrupt_before, interrupt_after, debug)   
960
         del fut, task   
962
# panic on failure or timeout-->
963
_panic_or_proceed(done, inflight, step)   
964
# don't keep futures around in memory longer than needed   
965
del done, inflight, futures File
d:\agentenv\Lib\site-packages\langgraph\pregel\__init__.py:1489
, in _panic_or_proceed(done, inflight, step)  
1487
             inflight.pop().cancel()  
1488
         # raise the exception->
1489
         raise exc  
1491
if inflight:  
1492
     # if we got here means we timed out  
1493
     while inflight:  
1494
         # cancel all pending tasks  File
C:\Program
Files\Python311\Lib\concurrent\futures\thread.py:58, in _WorkItem.run(self)    
55
     return    
57
try:--->
58
     result = self.fn(*self.args, **self.kwargs)    
59
except BaseException as exc:    
60
     self.future.set_exception(exc) File
d:\agentenv\Lib\site-packages\langgraph\pregel\retry.py:66
, in run_with_retry(task, retry_policy)    
64
task.writes.clear()    
65
# run the task--->
66
task.proc.invoke(task.input, task.config)    
67
# if successful, end    
68
break  File
d:\agentenv\Lib\site-packages\langchain_core\runnables\base.py:2493
, in RunnableSequence.invoke(self, input, config, **kwargs)  
2489
config = patch_config(  
2490
     config, callbacks=run_manager.get_child(f"seq:step:{i+1}")  
2491
)  
2492
if i == 0:->
2493
     input = step.invoke(input, config, **kwargs)  
2494
else:  
2495
     input = step.invoke(input, config) File
d:\agentenv\Lib\site-packages\langgraph\utils.py:95
, in RunnableCallable.invoke(self, input, config, **kwargs)    
93
     if accepts_config(self.func):    
94
         kwargs["config"] = config--->
95
     ret = context.run(self.func, input, **kwargs)    
96
if isinstance(ret, Runnable) and self.recurse:    
97
     return ret.invoke(input, config) Cell In[8],
line 90
    
88
model = llm    
89
model = model.bind_tools(tools)--->
90
response = model.invoke(messages)    
91
# We return a list, because this will get added to the existing list    
92
return {"messages": [response]} File
d:\agentenv\Lib\site-packages\langchain_core\runnables\base.py:4558
, in RunnableBindingBase.invoke(self, input, config, **kwargs)  
4552
def invoke(  
4553
     self,  
4554
     input: Input,  
4555
     config: Optional[RunnableConfig] = None,  
4556
     **kwargs: Optional[Any],  
4557
) -> Output:->
4558
     return self.bound.invoke(  
4559
         input,  
4560
         self._merge_configs(config),  
4561
         **{**self.kwargs, **kwargs},  
4562
     ) File
d:\agentenv\Lib\site-packages\langchain_core\language_models\chat_models.py:170
, in BaseChatModel.invoke(self, input, config, stop, **kwargs)   
159
def invoke(   
160
     self,   
161
     input: LanguageModelInput,   (...)   
165
     **kwargs: Any,   
166
) -> BaseMessage:   
167
     config = ensure_config(config)   
168
     return cast(   
169
         ChatGeneration,-->
170
         self.generate_prompt(   
171
             [self._convert_input(input)],   
172
             stop=stop,   
173
             callbacks=config.get("callbacks"),   
174
             tags=config.get("tags"),   
175
             metadata=config.get("metadata"),   
176
             run_name=config.get("run_name"),   
177
             run_id=config.pop("run_id", None),   
178
             **kwargs,   
179
         ).generations[0][0],   
180
     ).message File
d:\agentenv\Lib\site-packages\langchain_core\language_models\chat_models.py:599
, in BaseChatModel.generate_prompt(self, prompts, stop, callbacks, **kwargs)   
591
def generate_prompt(   
592
     self,   
593
     prompts: List[PromptValue],   (...)   
596
     **kwargs: Any,   
597
) -> LLMResult:   
598
     prompt_messages = [p.to_messages() for p in prompts]-->
599
     return self.generate(prompt_messages, stop=stop, callbacks=callbacks, **kwargs) File
d:\agentenv\Lib\site-packages\langchain_core\language_models\chat_models.py:456
, in BaseChatModel.generate(self, messages, stop, callbacks, tags, metadata, run_name, run_id, **kwargs)   
454
         if run_managers:   
455
             run_managers[i].on_llm_error(e, response=LLMResult(generations=[]))-->
456
         raise e   
457
flattened_outputs = [   
458
     LLMResult(generations=[res.generations], llm_output=res.llm_output)  # type: ignore[list-item]   
459
     for res in results   
460
]   
461
llm_output = self._combine_llm_outputs([res.llm_output for res in results]) File
d:\agentenv\Lib\site-packages\langchain_core\language_models\chat_models.py:446
, in BaseChatModel.generate(self, messages, stop, callbacks, tags, metadata, run_name, run_id, **kwargs)   
443
for i, m in enumerate(messages):   
444
     try:   
445
         results.append(-->
446
             self._generate_with_cache(   
447
                 m,   
448
                 stop=stop,   
449
                 run_manager=run_managers[i] if run_managers else None,   
450
                 **kwargs,   
451
             )   
452
         )   
453
     except BaseException as e:   
454
         if run_managers: File
d:\agentenv\Lib\site-packages\langchain_core\language_models\chat_models.py:671
, in BaseChatModel._generate_with_cache(self, messages, stop, run_manager, **kwargs)   
669
else:   
670
     if inspect.signature(self._generate).parameters.get("run_manager"):-->
671
         result = self._generate(   
672
             messages, stop=stop, run_manager=run_manager, **kwargs   
673
         )   
674
     else:   
675
         result = self._generate(messages, stop=stop, **kwargs) File
d:\langgraphmain\langgraphmain\examples\rag\utils\agentwrapper.py:1060
, in IAS_ChatModelOpen._generate(self, messages, stop, run_manager, **kwargs)  
1058
message_dicts, params = self._create_message_dicts(messages, stop)  
1059
params = {**params, **kwargs}->
1060
response = self.client.create(messages=message_dicts, **params)  
1061
return self._create_chat_result(response)
