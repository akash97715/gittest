[11:40 PM] Deep, Akash (External)
July 21, 2024 > 18:09:14 | INFO | utils.ias_openai_langchain:ias_openai_chat_completion_with_tools:368 | Calling chat completion endpoint with tools July 21, 2024 > 18:09:14 | INFO | utils.ias_openai_langchain:ias_openai_chat_completion_with_tools:369 | {'engine': 'gpt-4', 'messages': [{'role': 'system', 'content': 'You are a helpful assistant'}, {'role': 'user', 'content': 'Hello! How can I assist you today?'}, {'role': 'assistant', 'content': 'Hi'}, {'role': 'user', 'content': 'what is the weather in india'}], 'temperature': 0.7, 'max_tokens': 3000, 'tools': {}, 'tool_choice': 'auto'} July 21, 2024 > 18:09:15 | INFO | utils.ias_openai_langchain:ias_openai_chat_completion_with_tools:373 | Received response from llm July 21, 2024 > 18:09:15 | INFO | utils.ias_openai_langchain:ias_openai_chat_completion_with_tools:374 | {'detail': [{'type': 'list_type', 'loc': ['body', 'tools'], 'msg': 'Input should be a valid list', 'input': {}}]} July 21, 2024 > 18:09:15 | ERROR | utils.ias_openai_langchain:ias_openai_chat_completion_with_tools:377 | Error calling OpenAI chat completion API: 422, {'detail': [{'type': 'list_type', 'loc': ['body', 'tools'], 'msg': 'Input should be a valid list', 'input': {}}]} July 21, 2024 > 18:09:15 | ERROR | utils.ias_openai_langchain:ias_openai_chat_completion_with_tools:389 | Got the Exception
 
[11:45 PM] Deep, Akash (External)
class ChatRequest(BaseModel):
    engine: str
    messages: List[ChatMessage]
    temperature: float = Field(0, ge=0, le=1)
    max_tokens: int
    n: Optional[int] = Field(default=1, ge=1)
    stream: Optional[bool] = False
    stop: Optional[Union[str, list[str]]] = None
    logit_bias: Optional[Dict[str, int]] = None
    frequency_penalty: Optional[float] = Field(default=0, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=0, ge=-2.0, le=2.0)
    tools: Optional[List[ChatCompletionToolParam]] = None
    tool_choice: Optional[str] = None
    enhancements: Optional[Enhancements] = None
    dataSources: Optional[List[DataSource]] = None
 
