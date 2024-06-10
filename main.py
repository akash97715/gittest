from typing import List, Optional, Any, Dict, Union, Tuple, Iterator, AsyncIterator, Sequence, Mapping
from pydantic import Field, BaseModel, SecretStr
import json
import os
import sys
from functools import partial
from your_module import BaseChatModel, BaseMessage, AIMessage, HumanMessage, SystemMessage, FunctionMessage, ToolMessage, CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun, ChatGeneration, ChatResult, ChatGenerationChunk, UsageMetadata, Runnable, RunnablePassthrough, RunnableMap, convert_to_openai_function, convert_to_openai_tool, get_pydantic_field_names, build_extra_kwargs, convert_dict_to_message as _convert_dict_to_message, convert_message_to_dict as _convert_message_to_dict, agenerate_from_stream, generate_from_stream, get_from_dict_or_env, convert_to_secret_str, is_anthropic_model, logger, ias_openai_chat_completion_with_tools, aget_auth_token, httpx_client, IAS_OPENAI_CHAT_URL, GenericException


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
    context: Optional[List[str]] = None

    class Config:
        arbitrary_types_allowed = True

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        messages_dict = [convert_message_to_dict(s) for s in messages]

        if self.context:
            chat_history = create_chat_history_array(self.context)
            messages_dict[1:1] = chat_history

        if not is_anthropic_model(str(self.engine)):
            all_msgs = "".join(message["content"] for message in messages_dict)
            token_consumed = (
                self.get_num_tokens(f"{all_msgs}{self.user_query}{json.dumps(kwargs.get('tools', ''))}")
                + self.min_response_token
            )
            if self.max_tokens - token_consumed <= 0:
                token_consumed = 0

            logger.info(f"total token by system_message, user_query, kwargs[tools] is - {token_consumed}")
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
            kwargs.get("tools"),
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

        if self.context:
            chat_history = create_chat_history_array(self.context)
            messages_dict[1:1] = chat_history

        if not is_anthropic_model(str(self.engine)):
            all_msgs = "".join(message["content"] for message in messages_dict)
            token_consumed = (
                self.get_num_tokens(f"{all_msgs}{self.user_query}{json.dumps(kwargs.get('tools', ''))}")
                + self.min_response_token
            )
            if self.max_tokens - token_consumed <= 0:
                token_consumed = 0

            logger.info(f"total token by system_message, user_query, kwargs[tools] is - {token_consumed}")
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
            kwargs.get("tools"),
            "auto",
        )
        logger.debug(f"Total tokens consumed: {total_token_completion}")

        self.total_consumed_token.append(total_token_completion)

        return self._create_chat_result(response)

    def _create_chat_result(
        self, response: Union[dict, str]
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

    def invoke(self, messages: List[BaseMessage], **kwargs: Any) -> ChatResult:
        return self._generate(messages, **kwargs)

    async def ainvoke(self, messages: List[BaseMessage], **kwargs: Any) -> ChatResult:
        return await self._agenerate(messages, **kwargs)

    def bind_functions(
        self,
        functions: Sequence[Union[Dict[str, Any], Callable, BaseTool]],
        function_call: Optional[Union[str, Literal["auto", "none"]]] = None,
        **kwargs: Any,
    ) -> Runnable:
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
                    "When specifying `function_call`, you must provide exactly one function."
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
        tools: Sequence[Union[Dict[str, Any], Callable, BaseTool]],
        tool_choice: Optional[Union[str, Literal["auto", "none", "required", "any"], bool]] = None,
        **kwargs: Any,
    ) -> Runnable:
        formatted_tools = [convert_to_openai_tool(tool) for tool in tools]
        if tool_choice:
            if isinstance(tool_choice, str):
                if tool_choice not in ("auto", "none", "any", "required"):
                    tool_choice = {"type": "function", "function": {"name": tool_choice}}
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

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "IAS_OpenAI"


def create_chat_history_array(context: List[str]) -> List[Dict[str, str]]:
    chat_context = context[::-1]
    chat_history = []

    for i, msg in enumerate(chat_context):
        role = "user" if i % 2 == 0 else "assistant"
        chat_history.append({"role": role, "content": msg})

    return chat_history


def convert_dict_to_message(_dict: Mapping[str, Any]) -> BaseMessage:
    role = _dict.get("role")
    id_ = _dict.get("id")
    if role == "user":
        return HumanMessage(content=_dict.get("content", ""), id=id_)
    elif role == "assistant":
        content = _dict.get("content", "") or ""
        additional_kwargs: Dict = {}
        if function_call := _dict.get("function_call"):
            additional_kwargs["function_call"] = dict(function_call)
        if tool_calls := _dict.get
