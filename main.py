import requests
from typing import List, Optional
import json
import backoff
import logger

# Assume GenericException and BaseMessage, BaseTool types are defined elsewhere
# Define is_http_4xx_error to decide when to give up on backoff
def is_http_4xx_error(exception):
    return isinstance(exception, GenericException) and 400 <= exception.status_code < 500

@backoff.on_exception(
    backoff.expo, GenericException, max_tries=20, max_time=60, giveup=is_http_4xx_error
)
def ias_openai_chat_completion_with_tools(
    engine: str,
    temperature: float,
    max_tokens: int,
    client_id: str = None,
    x_vsl_client_id: str = None,
    bearer_token: str = None,
    messages: List[BaseMessage] = None,
    tools: List[BaseTool] = None,
    tool_choice: str = None,
) -> (str, int):
    """
    Generates a chat completion response for OpenAI model
    :param token: auth token
    :param user_message: user's prompt
    :param engine: model capable for chat completion i.e. gpt*
    :param temperature: value 0-1 that tells model to be more precise or generative
    :param max_tokens: max tokens the prompt & response should be. It depends on the model's capacity
    :return: response from OpenAI model and total tokens used
    """
    try:
        # Ensure tools is a list even if None
        tools = tools if tools else []
        
        payload = {
            "engine": engine,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": tools
        }

        # Add tool_choice only if tools are not empty
        if tools and tool_choice:
            payload["tool_choice"] = tool_choice

        token = get_auth_token(bearer_token)
 
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        if x_vsl_client_id is not None:
            headers["x-vsl-client_id"] = x_vsl_client_id
        elif client_id is not None:
            headers["x-vsl-client_id"] = client_id
 
        logger.info("Calling chat completion endpoint with tools")
        logger.info(payload)
 
        response = requests.post(IAS_OPENAI_CHAT_URL, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the response is an HTTP 4XX or 5XX
 
        logger.info("Received response from llm")
        response_data = response.json()
        logger.info(response_data)
 
        chat_completion = response_data["result"]
        total_token_completion = int(response_data["totalTokens"])

        return chat_completion, total_token_completion
    except requests.exceptions.HTTPError as e:
        error_message = response.json()
        logger.error(f"Error calling OpenAI chat completion API: {response.status_code}, {error_message}")
        raise GenericException(
            f"Error calling OpenAI chat completion API: {response.status_code}, {error_message}",
            status_code=response.status_code,
        )
    except Exception as e:
        logger.error("Got the Exception", str(e))
        raise GenericException(str(e))

