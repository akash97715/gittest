from your_module import IAS_ChatModel, HumanMessage, AIMessage, SystemMessage

# Example initialization
chat_model = IAS_ChatModel(
    engine="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=100,
    user_query="What's the weather like today?",
    min_response_token=50,
    system_message="You are a helpful assistant.",
    client_id="client-id",
    x_vsl_client_id="x-client-id",
    bearer_token="your-bearer-token",
    context=["Hi", "Hello! How can I assist you today?"]
)

# Prepare messages
messages = [
    SystemMessage(content=chat_model.system_message),
    HumanMessage(content=chat_model.user_query)
]

# Call the invoke method
response = chat_model.invoke(messages=messages)
print(response)
