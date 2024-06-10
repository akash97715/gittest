class IAS_ChatCaller(IAS_ChatModel):
    """IAS Chat Model integration for custom use.

    Setup:
        Initialize the IAS_ChatCaller with appropriate parameters.

    Key init args — completion params:
        engine: str
            Name of the model engine to use.
        temperature: float
            Sampling temperature.
        max_tokens: int
            Max number of tokens to generate.
        user_query: str
            The user query string.
        min_response_token: int
            Minimum number of tokens for the response.
        system_message: Optional[str]
            Initial system message for the chat.
        client_id: Optional[str]
            Client identifier.
        x_vsl_client_id: Optional[str]
            VSL client identifier.
        bearer_token: Optional[str]
            Bearer token for authentication.
        context: Optional[List[BaseMessage]]
            Initial context for the chat.
        n: int
            Number of chat completions to generate for each prompt.
        streaming: bool
            Whether to stream the results or not.
    """
    
    def __init__(
        self,
        engine: str,
        temperature: float = 0.7,
        max_tokens: int = 150,
        user_query: str = "",
        min_response_token: int = 20,
        system_message: Optional[str] = None,
        client_id: Optional[str] = None,
        x_vsl_client_id: Optional[str] = None,
        bearer_token: Optional[str] = None,
        context: Optional[List[BaseMessage]] = None,
        n: int = 1,
        streaming: bool = False,
    ):
        super().__init__(
            engine=engine,
            temperature=temperature,
            max_tokens=max_tokens,
            user_query=user_query,
            min_response_token=min_response_token,
            system_message=system_message,
            client_id=client_id,
            x_vsl_client_id=x_vsl_client_id,
            bearer_token=bearer_token,
            context=context,
        )
        self.n = n
        self.streaming = streaming

    @root_validator(pre=True)
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = get_pydantic_field_names(cls)
        extra = values.get("model_kwargs", {})
        values["model_kwargs"] = build_extra_kwargs(extra, values, all_required_field_names)
        return values

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        if values.get("n", 1) < 1:
            raise ValueError("n must be at least 1.")
        if values.get("n", 1) > 1 and values.get("streaming", False):
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

# Example initialization
chat_caller = IAS_ChatCaller(
    engine="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=150,
    user_query="How can I integrate a chat model?",
    min_response_token=20,
    system_message="You are a helpful assistant.",
    client_id="client_123",
    x_vsl_client_id="vsl_456",
    bearer_token="your_bearer_token",
    context=[BaseMessage(role="system", content="You are a helpful assistant.")],
    n=1,
    streaming=False
)
