from langchain_core.output_parsers.base import OutputParserLike
from langchain_core.output_parsers.openai_tools import (
    JsonOutputKeyToolsParser,
    PydanticToolsParser,
    make_invalid_tool_call,
    parse_tool_call,
)
from langchain_core.output_parsers import (
    JsonOutputParser,
    PydanticOutputParser,
)
from operator import itemgetter
 
 
def _is_pydantic_class(obj: Any) -> bool:
    return isinstance(obj, type) and issubclass(obj, BaseModel)
 
 
_BM = TypeVar("_BM", bound=BaseModel)
_DictOrPydanticClass = Union[Dict[str, Any], Type[_BM]]
_DictOrPydantic = Union[Dict, _BM]
 
 
class IAS_ChatModel(BaseChatModel, BaseModel):
    engine: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int
    user_query: str = "Ask me something"
    total_consumed_token: List[int] = Field(default_factory=list)
    min_response_token: int = 200
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
 
        response, total_token_completion = await ias_openai_chat_completion_with_tools(
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
 
            token_consumed = 0
        else:
            token_consumed = 0
 
        response, total_token_completion = ias_openai_chat_completion_with_tools(
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
 
    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], Type[BaseModel], Callable, BaseTool]],
        *,
        tool_choice: Optional[
            Union[dict, str, Literal["auto", "none", "required", "any"], bool]
        ] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        """Bind tool-like objects to this chat model.
 
        Assumes model is compatible with OpenAI tool-calling API.
 
        Args:
            tools: A list of tool definitions to bind to this chat model.
                Can be  a dictionary, pydantic model, callable, or BaseTool. Pydantic
                models, callables, and BaseTools will be automatically converted to
                their schema dictionary representation.
            tool_choice: Which tool to require the model to call.
                Options are:
                name of the tool (str): calls corresponding tool;
                "auto": automatically selects a tool (including no tool);
                "none": does not call a tool;
                "any" or "required": force at least one tool to be called;
                True: forces tool call (requires `tools` be length 1);
                False: no effect;
 
                or a dict of the form:
                {"type": "function", "function": {"name": <<tool_name>>}}.
            **kwargs: Any additional parameters to pass to the
                :class:`~langchain.runnable.Runnable` constructor.
        """
 
        formatted_tools = [convert_to_openai_tool(tool) for tool in tools]
        if tool_choice:
            if isinstance(tool_choice, str):
                # tool_choice is a tool/function name
                if tool_choice not in ("auto", "none", "any", "required"):
                    tool_choice = {
                        "type": "function",
                        "function": {"name": tool_choice},
                    }
                # 'any' is not natively supported by OpenAI API.
                # We support 'any' since other models use this instead of 'required'.
                if tool_choice == "any":
                    tool_choice = "required"
            elif isinstance(tool_choice, bool):
                if len(tools) > 1:
                    raise ValueError(
                        "tool_choice=True can only be used when a single tool is "
                        f"passed in, received {len(tools)} tools."
                    )
                tool_choice = {
                    "type": "function",
                    "function": {"name": formatted_tools[0]["function"]["name"]},
                }
            elif isinstance(tool_choice, dict):
                tool_names = [
                    formatted_tool["function"]["name"]
                    for formatted_tool in formatted_tools
                ]
                if not any(
                    tool_name == tool_choice["function"]["name"]
                    for tool_name in tool_names
                ):
                    raise ValueError(
                        f"Tool choice {tool_choice} was specified, but the only "
                        f"provided tools were {tool_names}."
                    )
            else:
                raise ValueError(
                    f"Unrecognized tool_choice type. Expected str, bool or dict. "
                    f"Received: {tool_choice}"
                )
            kwargs["tool_choice"] = tool_choice
        return super().bind(tools=formatted_tools, **kwargs)
 
    def with_structured_output(
        self,
        schema: Optional[_DictOrPydanticClass] = None,
        *,
        method: Literal["function_calling", "json_mode"] = "function_calling",
        include_raw: bool = False,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, _DictOrPydantic]:
        """Model wrapper that returns outputs formatted to match the given schema.
 
        Args:
            schema: The output schema as a dict or a Pydantic class. If a Pydantic class
                then the model output will be an object of that class. If a dict then
                the model output will be a dict. With a Pydantic class the returned
                attributes will be validated, whereas with a dict they will not be. If
                `method` is "function_calling" and `schema` is a dict, then the dict
                must match the OpenAI function-calling spec or be a valid JSON schema
                with top level 'title' and 'description' keys specified.
            method: The method for steering model generation, either "function_calling"
                or "json_mode". If "function_calling" then the schema will be converted
                to an OpenAI function and the returned model will make use of the
                function-calling API. If "json_mode" then OpenAI's JSON mode will be
                used. Note that if using "json_mode" then you must include instructions
                for formatting the output into the desired schema into the model call.
            include_raw: If False then only the parsed structured output is returned. If
                an error occurs during model output parsing it will be raised. If True
                then both the raw model response (a BaseMessage) and the parsed model
                response will be returned. If an error occurs during output parsing it
                will be caught and returned as well. The final output is always a dict
                with keys "raw", "parsed", and "parsing_error".
 
        Returns:
            A Runnable that takes any ChatModel input and returns as output:
 
                If include_raw is True then a dict with keys:
                    raw: BaseMessage
                    parsed: Optional[_DictOrPydantic]
                    parsing_error: Optional[BaseException]
 
                If include_raw is False then just _DictOrPydantic is returned,
                where _DictOrPydantic depends on the schema:
 
                If schema is a Pydantic class then _DictOrPydantic is the Pydantic
                    class.
 
                If schema is a dict then _DictOrPydantic is a dict.
 
        Example: Function-calling, Pydantic schema (method="function_calling", include_raw=False):
            .. code-block:: python
 
                from langchain_openai import ChatOpenAI
                from langchain_core.pydantic_v1 import BaseModel
 
                class AnswerWithJustification(BaseModel):
                    '''An answer to the user question along with justification for the answer.'''
                    answer: str
                    justification: str
 
                llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
                structured_llm = llm.with_structured_output(AnswerWithJustification)
 
                structured_llm.invoke("What weighs more a pound of bricks or a pound of feathers")
 
                # -> AnswerWithJustification(
                #     answer='They weigh the same',
                #     justification='Both a pound of bricks and a pound of feathers weigh one pound. The weight is the same, but the volume or density of the objects may differ.'
                # )
 
        Example: Function-calling, Pydantic schema (method="function_calling", include_raw=True):
            .. code-block:: python
 
                from langchain_openai import ChatOpenAI
                from langchain_core.pydantic_v1 import BaseModel
 
                class AnswerWithJustification(BaseModel):
                    '''An answer to the user question along with justification for the answer.'''
                    answer: str
                    justification: str
 
                llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
                structured_llm = llm.with_structured_output(AnswerWithJustification, include_raw=True)
 
                structured_llm.invoke("What weighs more a pound of bricks or a pound of feathers")
                # -> {
                #     'raw': AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_Ao02pnFYXD6GN1yzc0uXPsvF', 'function': {'arguments': '{"answer":"They weigh the same.","justification":"Both a pound of bricks and a pound of feathers weigh one pound. The weight is the same, but the volume or density of the objects may differ."}', 'name': 'AnswerWithJustification'}, 'type': 'function'}]}),
                #     'parsed': AnswerWithJustification(answer='They weigh the same.', justification='Both a pound of bricks and a pound of feathers weigh one pound. The weight is the same, but the volume or density of the objects may differ.'),
                #     'parsing_error': None
                # }
 
        Example: Function-calling, dict schema (method="function_calling", include_raw=False):
            .. code-block:: python
 
                from langchain_openai import ChatOpenAI
                from langchain_core.pydantic_v1 import BaseModel
                from langchain_core.utils.function_calling import convert_to_openai_tool
 
                class AnswerWithJustification(BaseModel):
                    '''An answer to the user question along with justification for the answer.'''
                    answer: str
                    justification: str
 
                dict_schema = convert_to_openai_tool(AnswerWithJustification)
                llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
                structured_llm = llm.with_structured_output(dict_schema)
 
                structured_llm.invoke("What weighs more a pound of bricks or a pound of feathers")
                # -> {
                #     'answer': 'They weigh the same',
                #     'justification': 'Both a pound of bricks and a pound of feathers weigh one pound. The weight is the same, but the volume and density of the two substances differ.'
                # }
 
        Example: JSON mode, Pydantic schema (method="json_mode", include_raw=True):
            .. code-block::
 
                from langchain_openai import ChatOpenAI
                from langchain_core.pydantic_v1 import BaseModel
 
                class AnswerWithJustification(BaseModel):
                    answer: str
                    justification: str
 
                llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
                structured_llm = llm.with_structured_output(
                    AnswerWithJustification,
                    method="json_mode",
                    include_raw=True
                )
 
                structured_llm.invoke(
                    "Answer the following question. "
                    "Make sure to return a JSON blob with keys 'answer' and 'justification'.\n\n"
                    "What's heavier a pound of bricks or a pound of feathers?"
                )
                # -> {
                #     'raw': AIMessage(content='{\n    "answer": "They are both the same weight.",\n    "justification": "Both a pound of bricks and a pound of feathers weigh one pound. The difference lies in the volume and density of the materials, not the weight." \n}'),
                #     'parsed': AnswerWithJustification(answer='They are both the same weight.', justification='Both a pound of bricks and a pound of feathers weigh one pound. The difference lies in the volume and density of the materials, not the weight.'),
                #     'parsing_error': None
                # }
 
        Example: JSON mode, no schema (schema=None, method="json_mode", include_raw=True):
            .. code-block::
 
                from langchain_openai import ChatOpenAI
 
                structured_llm = llm.with_structured_output(method="json_mode", include_raw=True)
 
                structured_llm.invoke(
                    "Answer the following question. "
                    "Make sure to return a JSON blob with keys 'answer' and 'justification'.\n\n"
                    "What's heavier a pound of bricks or a pound of feathers?"
                )
                # -> {
                #     'raw': AIMessage(content='{\n    "answer": "They are both the same weight.",\n    "justification": "Both a pound of bricks and a pound of feathers weigh one pound. The difference lies in the volume and density of the materials, not the weight." \n}'),
                #     'parsed': {
                #         'answer': 'They are both the same weight.',
                #         'justification': 'Both a pound of bricks and a pound of feathers weigh one pound. The difference lies in the volume and density of the materials, not the weight.'
                #     },
                #     'parsing_error': None
                # }
 
 
        """  # noqa: E501
        if kwargs:
            raise ValueError(f"Received unsupported arguments {kwargs}")
        is_pydantic_schema = _is_pydantic_class(schema)
        if method == "function_calling":
            if schema is None:
                raise ValueError(
                    "schema must be specified when method is 'function_calling'. "
                    "Received None."
                )
            llm = self.bind_tools([schema], tool_choice=True)
            if is_pydantic_schema:
                output_parser: OutputParserLike = PydanticToolsParser(
                    tools=[schema], first_tool_only=True
                )
            else:
                key_name = convert_to_openai_tool(schema)["function"]["name"]
                output_parser = JsonOutputKeyToolsParser(
                    key_name=key_name, first_tool_only=True
                )
        elif method == "json_mode":
            llm = self.bind(response_format={"type": "json_object"})
            output_parser = (
                PydanticOutputParser(pydantic_object=schema)
                if is_pydantic_schema
                else JsonOutputParser()
            )
        else:
            raise ValueError(
                f"Unrecognized method argument. Expected one of 'function_calling' or "
                f"'json_format'. Received: '{method}'"
            )
 
        if include_raw:
            parser_assign = RunnablePassthrough.assign(
                parsed=itemgetter("raw") | output_parser, parsing_error=lambda _: None
            )
            parser_none = RunnablePassthrough.assign(parsed=lambda _: None)
            parser_with_fallback = parser_assign.with_fallbacks(
                [parser_none], exception_key="parsing_error"
            )
            return RunnableMap(raw=llm) | parser_with_fallback
        else:
            return llm | output_parser


---------------------------------------------------------------------------KeyError                                  Traceback (most recent call last) Cell In[21], line 2      1 inputs = {"input": "what is the weather in india", "chat_history": []}----> 2 app.invoke(inputs) File d:\docinsight_langgraph\docinsightlanggraph\Lib\site-packages\langgraph\pregel\__init__.py:1668, in Pregel.invoke(self, input, config, stream_mode, output_keys, input_keys, interrupt_before, interrupt_after, debug, **kwargs)   1666 else:   1667     chunks = []-> 1668 for chunk in self.stream(   1669     input,   1670     config,   1671     stream_mode=stream_mode,   1672     output_keys=output_keys,   1673     input_keys=input_keys,   1674     interrupt_before=interrupt_before,   1675     interrupt_after=interrupt_after,   1676     debug=debug,   1677     **kwargs,   1678 ):   1679     if stream_mode == "values":   1680         latest = chunk File d:\docinsight_langgraph\docinsightlanggraph\Lib\site-packages\langgraph\pregel\__init__.py:1111, in Pregel.stream(self, input, config, stream_mode, output_keys, input_keys, interrupt_before, interrupt_after, debug) 1108 del fut, task
...
   1141 )   1142 logger.debug(f"Total tokens consumed: {total_token_completion}")   1144 self.total_consumed_token.append(total_token_completion)KeyError: 'tools\
