@backoff.on_exception(
    backoff.expo, GenericException, max_tries=20, max_time=60, giveup=is_http_4xx_error
)
def ias_openai_chat_completion(
    user_message: str,
    engine: str,
    temperature: float,
    max_tokens: int,
    system_message: str = None,
    client_id: str = None,
    x_vsl_client_id: str = None,
    bearer_token: str = None,
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
            "messages": [
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
 
        if system_message:
            payload["messages"].insert(0, {"role": "system", "content": system_message})
 
        logger.debug(f'payload to ias_openai_chat_completion api =====> {payload}')
        token = get_auth_token(bearer_token)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        if x_vsl_client_id is not None:
            headers["x-vsl-client_id"] = x_vsl_client_id
        elif client_id is not None:
            headers["x-vsl-client_id"] = client_id
 
        logger.info("Calling chat completion endpoint")
        response = requests.post(IAS_OPENAI_CHAT_URL, headers=headers, json=payload)
 
        if response.status_code != 200:
            logger.error(
                f"Error calling OpenAI chat completion  API: {response.status_code}, {response.json()}"
            )
            raise GenericException(
                f"Error calling OpenAI chat completion API: {response.status_code}, {response.json()}",
                status_code=response.status_code,
            )
 
        logger.info("Received response from llm")
     
        logger.info(response.json())
        print("PAYLOAD RECEIVED FROM CHAT COMPLETEION")
        chat_completion = json.loads(response.json()["result"])["content"]
        temp=response.json()
        total_token=int(temp['totalTokens'])        
 
        return total_token,chat_completion
    except Exception as e:
        logger.error("Got the Exception", str(e))
        # raising backoff exception
        raise GenericException(e)
