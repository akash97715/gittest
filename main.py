[12:12 AM] Deep, Akash (External)
        response, total_token_completion = ias_openai_chat_completion_with_tools(
            self.engine,
            self.temperature,
            self.max_tokens - token_consumed,
            self.client_id,
            self.x_vsl_client_id,
            self.bearer_token,
            messages_dict,
            kwargs.get("tools",[]),
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
 
[12:18 AM] Deep, Akash (External)
def convert_dict_to_message(_dict: Mapping[str, Any]) -> BaseMessage:
    """Convert a dictionary to a LangChain message.
 
    Args:
        _dict: The dictionary.
 
    Returns:
        The LangChain message.
    """
    role = _dict.get("role")
    id_ = _dict.get("id")
    if role == "user":
        return HumanMessage(content=_dict.get("content", ""), id=id_)
    elif role == "assistant":
        # Fix for azure
        # Also OpenAI returns None for tool invocations
        content = _dict.get("content", "") or ""
        additional_kwargs: Dict = {}
        if function_call := _dict.get("function_call"):
            additional_kwargs["function_call"] = dict(function_call)
        if tool_calls := _dict.get("tool_calls"):
            additional_kwargs["tool_calls"] = tool_calls
        return AIMessage(content=content, additional_kwargs=additional_kwargs, id=id_)
    elif role == "system":
        return SystemMessage(content=_dict.get("content", ""), id=id_)
    elif role == "function":
        return FunctionMessage(
            content=_dict.get("content", ""), name=_dict.get("name"), id=id_
        )
    elif role == "tool":
        additional_kwargs = {}
        if "name" in _dict:
            additional_kwargs["name"] = _dict["name"]
        return ToolMessage(
            content=_dict.get("content", ""),
            tool_call_id=_dict.get("tool_call_id"),
            additional_kwargs=additional_kwargs,
            id=id_,
        )
    else:
        return ChatMessage(content=_dict.get("content", ""), role=role, id=id_)
 
