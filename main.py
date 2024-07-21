# Ensure the function outputs data in a format that can be directly used by Pregel.stream
def ias_openai_chat_completion_with_tools(...):
    # existing setup code ...
    response_data = response.json()
    # Assuming response_data['result'] is a JSON string that needs parsing
    chat_completion = json.loads(response_data.get("result", "{}"))
    total_token_completion = int(response_data.get("totalTokens", 0))

    # Convert chat completion data to expected format if necessary
    # Assuming chat_completion is a dictionary that needs to be converted into a list of dictionaries
    messages = convert_api_response_to_messages(chat_completion)
    return messages, total_token_completion

def convert_api_response_to_messages(data):
    # This function should adapt depending on the actual structure of data
    # Example transformation
    return [{
        "role": data.get("role", "assistant"),
        "content": data.get("content", ""),
        "id": data.get("id", "default_id")
    }]
