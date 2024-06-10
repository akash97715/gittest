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
