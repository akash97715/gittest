class IAS_ChatModel(BaseChatModel,BaseModel):
    engine: str ='gpt-4'
    temperature: float =0.7
    max_tokens: int
    streaming: bool = False
    n: int = 2
    user_query: str = "Ask me something"
    total_consumed_token: List[int] = Field(default_factory=list)
    min_response_token: int =200
    system_message: Optional[str] = (None,)
    client_id: str = (None,)
    x_vsl_client_id: str = None
    bearer_token: str = None
    context: list = None
 
    class Config:
        arbitrary_types_allowed = True    
    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        params = {
            "model": self.engine,
            "stream": self.streaming,
            "n": self.n,
            "temperature": self.temperature,
            **self.model_kwargs,
        }
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        return params
