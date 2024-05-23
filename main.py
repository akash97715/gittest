def ias_openai_embeddings(
    raw_text:list,
    engine: str,
    client_id: str = None,
    x_vsl_client_id: str = None,
    bearer_token: str = None,
):
    try:
        url = IAS_EMBEDDINGS_URL
        payload = {"input": raw_text, "engine": engine}
        token = get_auth_token(bearer_token)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
 
        if x_vsl_client_id is not None:
            headers["x-vsl-client_id"] = x_vsl_client_id
        elif client_id is not None:
            headers["x-vsl-client_id"] = client_id
 
        logger.info("Triggering embedding endpoint")
        response = requests.post(url, headers=headers, json=payload)
 
        if response.status_code != 200:
            logger.error(
                f"Error calling OpenAI embedding API: {response.status_code}, {response.json()}"
            )
            raise GenericException(
                f"Error calling OpenAI embedding API: {response.status_code}, {response.json()}",
                status_code=response.status_code,
            )
 
        embeddings = json.loads(response.json()["result"])
        temp=response.json()
        total_token=temp['totalTokens']        
        logger.info("Recevied response from embedding endpoint")
 
        return embeddings,total_token
    except Exception as e:
        logger.error("Got the Exception", str(e))
        # raising backoff exception
        raise GenericException(e
