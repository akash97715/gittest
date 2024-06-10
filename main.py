from pydantic import BaseModel, Field, root_validator
from typing import Any, Dict, List, Optional
from loguru import logger
from abc import ABC

# Define the helper functions
def get_pydantic_field_names(cls) -> List[str]:
    return [field.alias for field in cls.__fields__.values()]

def build_extra_kwargs(extra: dict, values: dict, all_required_field_names: List[str]) -> dict:
    return {k: v for k, v in extra.items() if k not in all_required_field_names}

class BaseChatModel(BaseLanguageModel[BaseMessage], ABC):
    """Base class for Chat models."""

    callback_manager: Optional[BaseCallbackManager] = Field(default=None, exclude=True)
    """[DEPRECATED] Callback manager to add to the run trace."""

    @root_validator()
    def raise_deprecation(cls, values: Dict) -> Dict:
        """Raise deprecation warning if callback_manager is used."""
        if values.get("callback_manager") is not None:
            warnings.warn(
                "callback_manager is deprecated. Please use callbacks instead.",
                DeprecationWarning,
            )
            values["callbacks"] = values.pop("callback_manager", None)
        return values

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    # --- Runnable methods ---

    @property
    def OutputType(self) -> Any:
        """Get the output type for this runnable."""
        return AnyMessage

# Assuming these classes and methods exist and are imported correctly
class BaseLanguageModel(ABC):
    pass

class BaseMessage(BaseModel):
    role: str
    content: str

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
    n: int = 1
    streaming: bool = False

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
        if values.get("n", 1) < 1:
            raise ValueError("n must be at least 1.")
        if values.get("n", 1) > 1 and values.get("streaming", False):
            raise ValueError("n must be 1 when streaming.")
        return values

    # Existing methods

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
            n=n,
            streaming=streaming
        )

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
