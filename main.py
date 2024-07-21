import json
import requests

def ias_openai_chat_completion_with_tools(
    engine: str, temperature: float, max_tokens: int, client_id: Optional[str] = None,
    x_vsl_client_id: Optional[str] = None, bearer_token: Optional[str] = None,
    messages: Optional[List[dict]] = None, tools: Optional[List[dict]] = None,
    tool_choice: Optional[str] = None,
) -> (List[dict], int):
    """
    Calls the OpenAI chat completion endpoint and returns formatted messages and token count.
    """
    try:
        payload = {
            "engine": engine,
            "messages": messages or [],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": tools or [],
        }
        if tools and tool_choice:
            payload["tool_choice"] = tool_choice

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }
        if x_vsl_client_id:
            headers["x-vsl-client_id"] = x_vsl_client_id
        elif client_id:
            headers["x-vsl-client_id"] = client_id

        response = requests.post('http://api_endpoint_here', headers=headers, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad requests
        response_data = response.json()

        # Parse the result which is expected to be a JSON string
        result = json.loads(response_data.get('result', '{}')) if isinstance(response_data.get('result'), str) else response_data.get('result', {})
        messages = convert_api_response_to_messages(result)
        total_token_completion = int(response_data.get("totalTokens", 0))

        return messages, total_token_completion
    except requests.HTTPError as e:
        # Handle HTTP errors
        raise GenericException(f"HTTP Error: {str(e)}")
    except Exception as e:
        # Handle other exceptions
        raise GenericException(f"Unexpected error: {str(e)}")

def convert_api_response_to_messages(data):
    """
    Converts API response data into a list of message dictionaries.
    """
    return [{
        "role": data.get("role", "assistant"),
        "content": data.get("content", ""),
        "id": data.get("id", "default_id")
    }]
