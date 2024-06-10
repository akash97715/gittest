from pydantic import BaseModel, Field, SecretStr, root_validator
from typing import Any, Dict, List, Optional, Union, Tuple, AsyncIterator, Iterator, Literal, Sequence, Callable, Mapping
from pydantic.types import SecretStr
import os
import httpx
import json
from loguru import logger
from some_module import (
    BaseChatModel,
    BaseMessage,
    AIMessageChunk,
    ChatResult,
    ChatGeneration,
    convert_message_to_dict,
    convert_dict_to_message,
    UsageMetadata,
    LangSmithParams,
    BaseTool,
    _FunctionCall,
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
    generate_from_stream,
    agenerate_from_stream,
    convert_to_secret_str,
    get_from_dict_or_env,
    convert_to_openai_tool,
    convert_to_openai_function,
    RunnablePassthrough,
    RunnableMap,
    _is_pydantic_class,
    _DictOrPydantic,
    PydanticOutputParser,
    JsonOutputParser,
    JsonOutputKeyToolsParser,
    PydanticToolsParser,
    itemgetter,
    AIMessage,
)

class IAS_ChatModel(BaseChatModel, BaseModel):
    engine: str
    temperature: float
    max_tokens: int
    user_query: str
    total_consumed_token: List[int] = Field(default_factory=list)
    min_response_token: int
    system_message: Optional[str] = None
    client_id: Optional[str] = None
    x_vsl_client_id: Optional[str] = None
    bearer_token: Optional[str] = None
    context: Optional[List[BaseMessage]] = None

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = get_pydantic_field_names(cls)
        extra = values.get("model_kwargs", {})
        values["model_kwargs"] = build_extra_kwargs(extra, values, all_required_field_names)
        return values

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        if values["n"] < 1:
            raise ValueError("n must be at least 1.")
        if values["n"] > 1 and values["streaming"]:
            raise ValueError("n must be 1 when streaming.")

        values["openai_api_key"] = convert_to_secret_str(
            get_from_dict_or_env(values, "openai_api_key", "OPENAI_API_KEY")
        )
        values["openai_organization"] = (
            values["openai_organization"] or os.getenv("OPENAI_ORG_ID") or os.getenv("OPENAI_ORGANIZATION")
        )
        values["openai_api_base"] = values["openai_api_base"] or os.getenv("OPENAI_API_BASE")
        values["openai_proxy"] = get_from_dict_or_env(
            values, "openai_proxy", "OPENAI_PROXY", default=""
        )

        client_params = {
            "api_key": (
                values["openai_api_key"].get_secret_value()
                if values["openai_api_key"]
                else None
            ),
            "organization": values["openai_organization"],
            "base_url": values["openai_api_base"],
            "timeout": values["request_timeout"],
            "max_retries": values["max_retries"],
            "default_headers": values["default_headers"],
            "default_query": values["default_query"],
        }

        openai_proxy = values["openai_proxy"]
        if not values.get("client"):
            if openai_proxy and not values["http_client"]:
                try:
                    import httpx
                except ImportError as e:
                    raise ImportError(
                        "Could not import httpx python package. "
                        "Please install it with `pip install httpx`."
                    ) from e
                values["http_client"] = httpx.Client(proxy=openai_proxy)
            sync_specific = {"http_client": values["http_client"]}
            values["client"] = openai.OpenAI(
                **client_params, **sync_specific
            ).chat.completions
        if not values.get("async_client"):
            if openai_proxy and not values["http_async_client"]:
                try:
                    import httpx
                except ImportError as e:
                    raise ImportError(
                        "Could not import httpx python package. "
                        "Please install it with `pip install httpx`."
                    ) from e
                values["http_async_client"] = httpx.AsyncClient(proxy=openai_proxy)
            async_specific = {"http_client": values["http_async_client"]}
            values["async_client"] = openai.AsyncOpenAI(
                **client_params, **async_specific
            ).chat.completions
        return values

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        params = {
            "model": self.model_name,
            "stream": self.streaming,
            "n": self.n,
            "temperature": self.temperature,
            **self.model_kwargs,
        }
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        return params

    def _combine_llm_outputs(self, llm_outputs: List[Optional[dict]]) -> dict:
        overall_token_usage: dict = {}
        system_fingerprint = None
        for output in llm_outputs:
            if output is None:
                continue
            token_usage = output["token_usage"]
            if token_usage is not None:
                for k, v in token_usage.items():
                    if k in overall_token_usage:
                        overall_token_usage[k] += v
                    else:
                        overall_token_usage[k] = v
            if system_fingerprint is None:
                system_fingerprint = output.get("system_fingerprint")
        combined = {"token_usage": overall_token_usage, "model_name": self.model_name}
        if system_fingerprint:
            combined["system_fingerprint"] = system_fingerprint
        return combined

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs, "stream": True}

        default_chunk_class = AIMessageChunk
        with self.client.create(messages=message_dicts, **params) as response:
            for chunk in response:
                if not isinstance(chunk, dict):
                    chunk = chunk.model_dump()
                if len(chunk["choices"]) == 0:
                    if token_usage := chunk.get("usage"):
                        usage_metadata = UsageMetadata(
                            input_tokens=token_usage.get("prompt_tokens", 0),
                            output_tokens=token_usage.get("completion_tokens", 0),
                            total_tokens=token_usage.get("total_tokens", 0),
                        )
                        chunk = ChatGenerationChunk(
                            message=default_chunk_class(
                                content="", usage_metadata=usage_metadata
                            )
                        )
                    else:
                        continue
                else:
                    choice = chunk["choices"][0]
                    if choice["delta"] is None:
                        continue
                    chunk = _convert_delta_to_message_chunk(
                        choice["delta"], default_chunk_class
                    )
                    generation_info = {}
                    if finish_reason := choice.get("finish_reason"):
                        generation_info["finish_reason"] = finish_reason
                    logprobs = choice.get("logprobs")
                    if logprobs:
                        generation_info["logprobs"] = logprobs
                    default_chunk_class = chunk.__class__
                    chunk = ChatGenerationChunk(
                        message=chunk, generation_info=generation_info or None
                    )
                if run_manager:
                    run_manager.on_llm_new_token(
                        chunk.text, chunk=chunk, logprobs=logprobs
                    )
                yield chunk

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.streaming:
            stream_iter = self._stream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return generate_from_stream(stream_iter)
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        response = self.client.create(messages=message_dicts, **params)
        return self._create_chat_result(response)

    def _create_message_dicts(
        self, messages: List[BaseMessage], stop: Optional[List[str]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        params = self._default_params
        if stop is not None:
            if "stop" in params:
                raise ValueError("`stop` found in both the input and default params.")
            params["stop"] = stop
        message_dicts = [_convert_message_to_dict(m) for m in messages]
        return message_dicts, params

    def _create_chat_result(
        self, response: Union[dict, openai.BaseModel]
    ) -> ChatResult:
        generations = []
        if not isinstance(response, dict):
            response = response.model_dump()

        if response.get("error"):
            raise ValueError(response.get("error"))

        token_usage = response.get("usage", {})
        for res in response["choices"]:
            message = _convert_dict_to_message(res["message"])
            if token_usage and isinstance(message, AIMessage):
                message.usage_metadata = {
                    "input_tokens": token_usage.get("prompt_tokens", 0),
                    "output_tokens": token_usage.get("completion_tokens", 0),
                    "total_tokens": token_usage.get("total_tokens", 0),
                }
            generation_info = dict(finish_reason=res.get("finish_reason"))
            if "logprobs" in res:
                generation_info["logprobs"] = res["logprobs"]
            gen = ChatGeneration(
                message=message,
                generation_info=generation_info,
            )
            generations.append(gen)
        llm_output = {
            "token_usage": token_usage,
            "model_name": response.get("model", self.model_name),
            "system_fingerprint": response.get("system_fingerprint", ""),
        }
        return ChatResult(generations=generations, llm_output=llm_output)

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs, "stream": True}

        default_chunk_class = AIMessageChunk
        response = await self.async_client.create(messages=message_dicts, **params)
        async with response:
            async for chunk in response:
                if not isinstance(chunk, dict):
                    chunk = chunk.model_dump()
                if len(chunk["choices"]) == 0:
                    if token_usage := chunk.get("usage"):
                        usage_metadata = UsageMetadata(
                            input_tokens=token_usage.get("prompt_tokens", 0),
                            output_tokens=token_usage.get("completion_tokens", 0),
                            total_tokens=token_usage.get("total_tokens", 0),
                        )
                        chunk = ChatGenerationChunk(
                            message=default_chunk_class(
                                content="", usage_metadata=usage_metadata
                            )
                        )
                    else:
                        continue
                else:
                    choice = chunk["choices"][0]
                    if choice["delta"] is None:
                        continue
                    chunk = _convert_delta_to_message_chunk(
                        choice["delta"], default_chunk_class
                    )
                    generation_info = {}
                    if finish_reason := choice.get("finish_reason"):
                        generation_info["finish_reason"] = finish_reason
                    logprobs = choice.get("logprobs")
                    if logprobs:
                        generation_info["logprobs"] = logprobs
                    default_chunk_class = chunk.__class__
                    chunk = ChatGenerationChunk(
                        message=chunk, generation_info=generation_info or None
                    )
                if run_manager:
                    await run_manager.on_llm_new_token(
                        token=chunk.text, chunk=chunk, logprobs=logprobs
                    )
                yield chunk

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.streaming:
            stream_iter = self._astream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return await agenerate_from_stream(stream_iter)

        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        response = await self.async_client.create(messages=message_dicts, **params)
        return self._create_chat_result(response)

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model_name": self.model_name, **self._default_params}

    def _get_invocation_params(
        self, stop: Optional[List[str]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            **super()._get_invocation_params(stop=stop),
            **self._default_params,
            **kwargs,
        }

    def _get_ls_params(
        self, stop: Optional[List[str]] = None, **kwargs: Any
    ) -> LangSmithParams:
        params = self._get_invocation_params(stop=stop, **kwargs)
        ls_params = LangSmithParams(
            ls_provider="openai",
            ls_model_name=self.model_name,
            ls_model_type="chat",
            ls_temperature=params.get("temperature", self.temperature),
        )
        if ls_max_tokens := params.get("max_tokens", self.max_tokens):
            ls_params["ls_max_tokens"] = ls_max_tokens
        if ls_stop := stop or params.get("stop", None):
            ls_params["ls_stop"] = ls_stop
        return ls_params

    @property
    def _llm_type(self) -> str:
        return "IAS_OpenAI"

    def _get_encoding_model(self) -> Tuple[str, tiktoken.Encoding]:
        if self.tiktoken_model_name is not None:
            model = self.tiktoken_model_name
        else:
            model = self.model_name
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            model = "cl100k_base"
            encoding = tiktoken.get_encoding(model)
        return model, encoding

    def get_token_ids(self, text: str) -> List[int]:
        if self.custom_get_token_ids is not None:
            return self.custom_get_token_ids(text)
        if sys.version_info[1] <= 7:
            return super().get_token_ids(text)
        _, encoding_model = self._get_encoding_model()
        return encoding_model.encode(text)

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        if sys.version_info[1] <= 7:
            return super().get_num_tokens_from_messages(messages)
        model, encoding = self._get_encoding_model()
        if model.startswith("gpt-3.5-turbo-0301"):
            tokens_per_message = 4
            tokens_per_name = -1
        elif model.startswith("gpt-3.5-turbo") or model.startswith("gpt-4"):
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(
                f"get_num_tokens_from_messages() is not presently implemented "
                f"for model {model}. See "
                "https://platform.openai.com/docs/guides/text-generation/managing-tokens"
                " for information on how messages are converted to tokens."
            )
        num_tokens = 0
        messages_dict = [_convert_message_to_dict(m) for m in messages]
        for message in messages_dict:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3
        return num_tokens

    def bind_functions(
        self,
        functions: Sequence[Union[Dict[str, Any], Type[BaseModel], Callable, BaseTool]],
        function_call: Optional[
            Union[_FunctionCall, str, Literal["auto", "none"]]
        ] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        formatted_functions = [convert_to_openai_function(fn) for fn in functions]
        if function_call is not None:
            function_call = (
                {"name": function_call}
                if isinstance(function_call, str)
                and function_call not in ("auto", "none")
                else function_call
            )
            if isinstance(function_call, dict) and len(formatted_functions) != 1:
                raise ValueError(
                    "When specifying `function_call`, you must provide exactly one "
                    "function."
                )
            if (
                isinstance(function_call, dict)
                and formatted_functions[0]["name"] != function_call["name"]
            ):
                raise ValueError(
                    f"Function call {function_call} was specified, but the only "
                    f"provided function was {formatted_functions[0]['name']}."
                )
            kwargs = {**kwargs, "function_call": function_call}
        return super().bind(
            functions=formatted_functions,
            **kwargs,
        )

    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], Type[BaseModel], Callable, BaseTool]],
        *,
        tool_choice: Optional[
            Union[dict, str, Literal["auto", "none", "required", "any"], bool]
        ] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        formatted_tools = [convert_to_openai_tool(tool) for tool in tools]
        if tool_choice:
            if isinstance(tool_choice, str):
                if tool_choice not in ("auto", "none", "any", "required"):
                    tool_choice = {
                        "type": "function",
                        "function": {"name": tool_choice},
                    }
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

    @overload
    def with_structured_output(
        self,
        schema: Optional[_DictOrPydanticClass] = None,
        *,
        method: Literal["function_calling", "json_mode"] = "function_calling",
        include_raw: Literal[True] = True,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, _AllReturnType]:
        ...

    @overload
    def with_structured_output(
        self,
        schema: Optional[_DictOrPydanticClass] = None,
        *,
        method: Literal["function_calling", "json_mode"] = "function_calling",
        include_raw: Literal[False] = False,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, _DictOrPydantic]:
        ...

    def with_structured_output(
        self,
        schema: Optional[_DictOrPydanticClass] = None,
        *,
        method: Literal["function_calling", "json_mode"] = "function_calling",
        include_raw: bool = False,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, _DictOrPydantic]:
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

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Top Level call"""
        messages_dict = [convert_message_to_dict(s) for s in messages]

        if self.context:
            chat_history = create_chat_history_array(self.context)
            messages_dict[1:1] = chat_history

        if not is_anthropic_model(str(self.engine)):
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
