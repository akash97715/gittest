from pydantic import BaseModel, Field, root_validator
from typing import List, Dict, Optional, Any, Union, Tuple, Sequence, Callable, Iterator, AsyncIterator, Literal
import json
import httpx
from some_module import (
    BaseChatModel, BaseMessage, ChatResult, ChatGeneration, ChatGenerationChunk,
    convert_message_to_dict, convert_dict_to_message, AIMessageChunk, UsageMetadata,
    LangSmithParams, PydanticToolsParser, JsonOutputKeyToolsParser, PydanticOutputParser,
    JsonOutputParser, RunnablePassthrough, RunnableMap, Runnable, get_from_dict_or_env,
    convert_to_openai_function, convert_to_openai_tool, build_extra_kwargs,
    get_pydantic_field_names, ensure_config, generate_from_stream, agenerate_from_stream,
    create_chat_history_array, is_anthropic_model
)
from another_module import aget_auth_token, IAS_OPENAI_CHAT_URL, logger, GenericException

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
    context: Optional[list] = None

    request_timeout: Union[float, Tuple[float, float], Any, None] = None
    max_retries: int = 2
    streaming: bool = False
    n: int = 1
    tiktoken_model_name: Optional[str] = None
    default_headers: Union[Dict[str, str], None] = None
    default_query: Union[Dict[str, object], None] = None
    http_client: Union[Any, None] = None
    http_async_client: Union[Any, None] = None

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        all_required_field_names = get_pydantic_field_names(cls)
        extra = values.get("model_kwargs", {})
        values["model_kwargs"] = build_extra_kwargs(extra, values, all_required_field_names)
        return values

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        token = get_from_dict_or_env(values, "bearer_token", "BEARER_TOKEN")
        if not token:
            raise ValueError("Bearer token is required")
        values["bearer_token"] = token
        client_id = values.get("client_id")
        x_vsl_client_id = values.get("x_vsl_client_id")
        if not client_id and not x_vsl_client_id:
            raise ValueError("Either client_id or x_vsl_client_id must be provided")
        return values

    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[AsyncCallbackManagerForLLMRun] = None, **kwargs: Any) -> ChatResult:
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

            logger.info(f"total token by system_message, user_query, kwargs[tools] is - {token_consumed}")
        else:
            token_consumed = 0

        response, total_token_completion = await self.ias_openai_chat_completion_with_tools(
            self.engine,
            self.temperature,
            self.max_tokens - token_consumed,
            self.client_id,
            self.x_vsl_client_id,
            self.bearer_token,
            messages_dict,
            kwargs.get("tools"),
            "auto",
        )
        logger.debug(f"Total tokens consumed: {total_token_completion}")

        self.total_consumed_token.append(total_token_completion)

        return self._create_chat_result(response)

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> ChatResult:
        if self.streaming:
            stream_iter = self._stream(messages, stop=stop, run_manager=run_manager, **kwargs)
            return generate_from_stream(stream_iter)
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        response, total_token_completion = self.ias_openai_chat_completion_with_tools(
            self.engine,
            self.temperature,
            self.max_tokens - token_consumed,
            self.client_id,
            self.x_vsl_client_id,
            self.bearer_token,
            message_dicts,
            kwargs.get("tools"),
            "auto",
        )
        self.total_consumed_token.append(total_token_completion)
        return self._create_chat_result(response)

    def _create_chat_result(self, response: Union[dict, Any]) -> ChatResult:
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
        return "IAS_OpenAI"

    @property
    def _default_params(self) -> Dict[str, Any]:
        params = {
            "model": self.engine,
            "stream": self.streaming,
            "n": self.n,
            "temperature": self.temperature,
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
        combined = {"token_usage": overall_token_usage, "model_name": self.engine}
        if system_fingerprint:
            combined["system_fingerprint"] = system_fingerprint
        return combined

    def _stream(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> Iterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs, "stream": True}

        default_chunk_class = AIMessageChunk
        for chunk in self.ias_openai_chat_completion_with_tools(
            self.engine,
            self.temperature,
            self.max_tokens,
            self.client_id,
            self.x_vsl_client_id,
            self.bearer_token,
            message_dicts,
            kwargs.get("tools"),
            "auto",
        ):
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

    async def _astream(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[AsyncCallbackManagerForLLMRun] = None, **kwargs: Any) -> AsyncIterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs, "stream": True}

        default_chunk_class = AIMessageChunk
        response = await self.ias_openai_chat_completion_with_tools(
            self.engine,
            self.temperature,
            self.max_tokens,
            self.client_id,
            self.x_vsl_client_id,
            self.bearer_token,
            message_dicts,
            kwargs.get("tools"),
            "auto",
        )
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

    async def ias_openai_chat_completion_with_tools(
        self,
        engine: str,
        temperature: float,
        max_tokens: int,
        client_id: str = None,
        x_vsl_client_id: str = None,
        bearer_token: str = None,
        messages: List[BaseMessage] = None,
        tools: List[Any] = None,
        tool_choice: str = None,
    ) -> str:
        """
        Generates a chat completion response for OpenAI model
        """
        try:
            payload = {
                "engine": engine,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "tools": tools,
                "tool_choice": tool_choice,
            }

            token = await aget_auth_token(bearer_token)

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
            if x_vsl_client_id is not None:
                headers["x-vsl-client_id"] = x_vsl_client_id
            elif client_id is not None:
                headers["x-vsl-client_id"] = client_id

            logger.info("Calling chat completion endpoint with tools")
            logger.info(payload)

            async with httpx.AsyncClient() as client:
                response = await client.post(IAS_OPENAI_CHAT_URL, json=payload, headers=headers)

            logger.info("Received response from llm")
            logger.info(response.json())

            if response.status_code != 200:
                logger.error(
                    f"Error calling OpenAI chat completion API: {response.status_code}, {response.json()}"
                )
                raise GenericException(
                    f"Error calling OpenAI chat completion API: {response.status_code}, {response.json()}",
                    status_code=response.status_code,
                )
            chat_completion = json.loads(response.json()["result"])
            total_token_completion = int(response.json()['totalTokens'])
            return chat_completion, total_token_completion
        except Exception as e:
            logger.error("Got the Exception", str(e))
            # raising backoff exception
            raise GenericException(e)
