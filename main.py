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
