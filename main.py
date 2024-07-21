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
) -> str:
    """
    Generates a chat completion response for OpenAI model
    :param token: auth token
    :param user_message: user's prompt
    :param engine: model capable for chat completion i.e. gpt*
    :param temperature: value 0-1 that tells model to be more precise or generative
    :param max_tokens: max tokens the prompt & response should be. It depends on the model's capacity
    :return: response from OpenAI model
    """
    try:
        payload = {
            "engine": engine,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": tools,
            "tool_choice": tool_choice,
        }
 
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
 
        logger.info("Received response from llm")
        logger.info(response.json())
 
        if response.status_code != 200:
            logger.error(
                f"Error calling OpenAI chat completion API: {response.status_code}, {response.json()}"
            )
            raise GenericException(
                f"Error calling OpenAI chat completion API: {response.status_code}, {response.json()}",
                status_code=response.status_code,
            )
        chat_completion = json.loads(response.json()["result"])
 
        total_token_completion = int(response.json()["totalTokens"])
        return chat_completion, total_token_completion
    except Exception as e:
        logger.error("Got the Exception", str(e))
        # raising backoff exception
        raise GenericException(e)
