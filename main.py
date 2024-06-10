[2:01 PM] Deep, Akash (External)
Cell In[40], line 89     87 messages = state["messages"]     88 model = llm---> 89 model = model.bind_tools(tools)     90 response = model.invoke(messages)     91 # We return a list, because this will get added to the existing list  File d:\agentenv\Lib\site-packages\langchain_core\language_models\chat_models.py:951, in BaseChatModel.bind_tools(self, tools, **kwargs)    946 def bind_tools(    947     self,    948     tools: Sequence[Union[Dict[str, Any], Type[BaseModel], Callable, BaseTool]],    949     **kwargs: Any,    950 ) -> Runnable[LanguageModelInput, BaseMessage]:--> 951     raise NotImplementedError() NotImplementedError:
[2:03 PM] Deep, Akash (External)
class IAS_ChatModel(BaseChatModel,BaseModel):
    engine: str
    temperature: float
    max_tokens: int
    user_query: str
    total_consumed_token: List[int] = Field(default_factory=list)
    min_response_token: int
    system_message: Optional[str] = (None,)
    client_id: str = (None,)
    x_vsl_client_id: str = None
    bearer_token: str = None
    context: list = None
 
    class Config:
        arbitrary_types_allowed = True    
 
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Top Level call"""
        messages_dict = [convert_message_to_dict(s) for s in messages]
 
        # Create chat history array.
        if self.context:
            chat_history = create_chat_history_array(self.context)
            messages_dict[1:1] = chat_history
 
        if not is_anthropic_model(str(self.engine)):
            # Reduce max token based on token consumed
            all_msgs = ""
            for message in messages_dict:
                all_msgs += str(message["content"])
 
            token_consumed = (
                self.get_num_tokens(
                    (
                        "" + all_msgs + self.user_query + json.dumps(kwargs["tools"])
                        if kwargs["tools"]
                        else ""
                    )
                )
                + self.min_response_token
            )
            if self.max_tokens - token_consumed <= 0:
                token_consumed = 0
 
            logger.info(
                f"total token by system_message, user_query, kwargs[tools] is - {token_consumed}"
            )
        else:
            token_consumed = 0
 
        response ,total_token_completion= await ias_openai_chat_completion_with_tools(
            self.engine,
            self.temperature,
            self.max_tokens - token_consumed,
            self.client_id,
            self.x_vsl_client_id,
            self.bearer_token,
            messages_dict,
            kwargs["tools"],
            "auto",
        )
        logger.debug(f"Total tokens consumed: {total_token_completion}")
       
        self.total_consumed_token.append(total_token_completion)
 
       
 
        return self._create_chat_result(response)
 
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        pass
 
    def _create_chat_result(
        self, response: Union[dict, openai.BaseModel, str]
    ) -> ChatResult:
        generations = []
 
        gen = ChatGeneration(
            message=convert_dict_to_message(response),
            generation_info=dict(finish_reason="stop"),
        )
        generations.append(gen)
        llm_output = {
            "token_usage": 0,
            "model_name": self.engine,
        }
        return ChatResult(generations=generations, llm_output=llm_output)
 
    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "IAS_OpenAI"
