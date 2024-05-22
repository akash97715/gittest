class IASOpenaiConversationalLLM(LLM):
    """Wrapper for IAS secured OpenAI chat API"""
 
    engine: str
    temperature: float
    max_tokens: int
    total_consumed_token:list
    system_message: str = None
    client_id: str = None
    x_vsl_client_id: str = None
    bearer_auth: str = None
 
    def __init__(self, engine, client_id,total_consumed_token,temperature,max_tokens, system_message, x_vsl_client_id=None, bearer_auth=None):
        self.engine = engine
        self.total_consumed_token=total_consumed_token
        self.client_id = client_id
        self.temperature=temperature
        self.max_tokens=max_tokens
        self.x_vsl_client_id = x_vsl_client_id
        self.bearer_auth = bearer_auth  
        self.system_message=system_message
 
    @property
    def _llm_type(self) -> str:
        return "IAS_OpenAI"
 
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
    ) -> str:
 
        prompt_message = prompt
 
        if self.system_message:
            prompt_message = prompt_message + self.system_message
 
        token_consumed = self.get_num_tokens(prompt_message)
        response,totaltok = ias_openai_chat_completion(
            prompt,
            self.engine,
            self.temperature,
            calculate_max_tokens(self.max_tokens, str(self.engine), token_consumed),
            self.system_message,
            self.client_id,
            self.x_vsl_client_id,
        )
        self.total_consumed_token.append(totaltok)
        return response
 
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        params = {
            "engine": self.engine,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "total_consumed_token": self.total_consumed_token
        }
        return params


May 22, 2024 > 08:53:08 | ERROR | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.langchain.v1.helper:get_llm_response:728 | Request id:  | Index:  | MD5:  Filename:  | Failed while getting llm response
May 22, 2024 > 08:53:08 | ERROR | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.langchain.v1.api:search:182 | Request id:  | Index:  | MD5:  Filename:  | Error in invoke_search method. AttributeError("'IASOpenaiConversationalLLM' object has no attribute '__fields_set__'")
May 22, 2024 > 08:53:08 | ERROR | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.langchain.v1.api:search:186 | Request id:  | Index:  | MD5:  Filename:  | Error in search endpoint. AttributeError("'IASOpenaiConversationalLLM' object has no attribute '__fields_set__'")
May 22, 2024 > 08:53:08 | ERROR | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | main:timeout_middleware:122 | Request id:  | Index:  | MD5:  Filename:  | Main Exception - Human Request Error: 1.7139701843261719 seconds - /docinsight/search
May 22, 2024 > 08:53:08 | ERROR | Client id: 8bc3cc94aaad42169c5fd6fbd63ffb2f | app.utils.universal_exceptions:generic_exception_handler:60 | Request id:  | Index:  | MD5:  Filename:  | | status_code=500 | client_id=8bc3cc94aaad42169c5fd6fbd63ffb2f | error_type=AttributeError | error_code=realtime-backpropagation-dbed | msg_to_human=Aha! Something's made our server ponder. It's deep in thought. Please retry now or later. | url_path=/docinsight/search | exception='IASOpenaiConversationalLLM' object has no attribute '__fields_set__' | stack_trace=Traceback (most recent call last):
