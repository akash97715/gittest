ain:ias_openai_chat_completion:216 | Request id:  | Index:  | MD5:  Filename:  | payload to ias_openai_chat_completion api =====> {'engine': 'gpt-4-32k', 'messages': [{'role': 'user', 'content': "Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.\n\n        271\n\n271\n\n271\n\n157\n\n385\n\n        Question: 637\n        Helpful Answer:"}], 'temperature': 0.0, 'max_tokens': 15417}
May 22, 2024 > 09:54:06 | INFO | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.langchain.v1.utils.ias_openai_langchain:ias_openai_chat_completion:227 | Request id:  | Index:  | MD5:  Filename:  | Calling chat completion endpoint
May 22, 2024 > 09:54:09 | INFO | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.langchain.v1.utils.ias_openai_langchain:ias_openai_chat_completion:239 | Request id:  | Index:  | MD5:  Filename:  | Received response from llm
May 22, 2024 > 09:54:09 | INFO | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.langchain.v1.utils.ias_openai_langchain:ias_openai_chat_completion:241 | Request id:  | Index:  | MD5:  Filename:  | {'status': 'success', 'result': '{"content": "I don\'t know.", "role": "assistant"}', 'totalTokens': 73}
PAYLOAD RECEIVED FROM CHAT COMPLETEION
May 22, 2024 > 09:54:09 | ERROR | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.langchain.v1.helper:get_llm_response:729 | Request id:  | Index:  | MD5:  Filename:  | Failed while getting llm response
May 22, 2024 > 09:54:09 | ERROR | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.langchain.v1.api:search:182 | Request id:  | Index:  | MD5:  Filename:  | Error in invoke_search method. TypeError("unsupported operand type(s) for +: 'int' and 'str'")
May 22, 2024 > 09:54:09 | ERROR | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.langchain.v1.api:search:186 | Request id:  | Index:  | MD5:  Filename:  | Error in search endpoint. TypeError("unsupported operand type(s) for +: 'int' and 'str'")
May 22, 2024 > 09:54:09 | ERROR | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | main:timeout_middleware:122 | Request id:  | Index:  | MD5:  Filename:  | Main Exception - Human Request Error: 10.094133377075195 seconds - /docinsight/search
May 22, 2024 > 09:54:09 | ERROR | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.utils.universal_exceptions:generic_exception_handler:60 | Request id:  | Index:  | MD5:  Filename:  | | status_code=500 | client_id=8bc3cc94aaad42169c5fd6fbd63ffb2f | error_type=TypeError | error_code=cognitive-reduction-3361 | msg_to_human=Whoops! A bug flew into our system. Our service is gently shooing it away. Please try again later. | url_path=/docinsight/search | exception=unsupported operand type(s) for +: 'int' and 'str' | stack_trace=Traceback (most recent call last):
  File "D:\docinsightenv\Lib\site-packages\anyio\streams\memory.py", line 98, in receive
    return self.receive_nowait()
           ^^^^^^^^^^^^^^^^^^^^^
  File "D:\docinsightenv\Lib\site-packages\anyio\streams\memory.py", line 93, in receive_nowait
    raise WouldBlock
anyio.WouldBlock
 
During handling of the above exception, another exception occurred:
 
Traceback (most recent call last):
  File "D:\docinsightenv\Lib\site-packages\starlette\middleware\base.py", line 78, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\docinsightenv\Lib\site-packages\anyio\streams\memory.py", line 118, in receive
    raise EndOfStream
anyio.EndOfStream
 
During handling of the above exception, another exception occurred:
 
Traceback (most recent call last):
  File "D:\opensearchindexfix\vessel-services\docinsight\main.py", line 100, in timeout_middleware
    response = await asyncio.wait_for(
               ^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Program Files\Python311\Lib\asyncio\tasks.py", line 479, in wait_for
    return fut.result()
           ^^^^^^^^^^^^
  File "D:\docinsightenv\Lib\site-packages\starlette\middleware\base.py", line 84, in call_next
    raise app_exc
  File "D:\docinsightenv\Lib\site-packages\starlette\middleware\base.py", line 70, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "D:\docinsightenv\Lib\site-packages\starlette\middleware\cors.py", line 83, in __call__
    await self.app(scope, receive, send)
  File "D:\docinsightenv\Lib\site-packages\starlette\middleware\exceptions.py", line 79, in __call__
    raise exc
  File "D:\docinsightenv\Lib\site-packages\starlette\middleware\exceptions.py", line 68, in __call__
    await self.app(scope, receive, sender)
  File "C:\Program Files\Python311\Lib\contextlib.py", line 222, in __aexit__
    await self.gen.athrow(typ, value, traceback)
  File "D:\docinsightenv\Lib\site-packages\fastapi\concurrency.py", line 36, in contextmanager_in_threadpool
    raise e
TypeError: unsupported operand type(s) for +: 'int' and 'str'
|
INFO:     127.0.0.1:52761 - "POST /docinsight/search HTTP/1.1" 500 Internal Server Error
