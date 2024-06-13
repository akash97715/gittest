import pytz
import datetime
import json
from httpx import AsyncClient, HTTPException

async def stream_completion(client, input_request, user_data):
    stream_start = False

    logger.info("Streaming completion request")
    bearer_token = '0001P1lrDr2KSLQ50S6eqjytIFZp'
    url = "https://mule4api-comm-amer-dev.pfizer.com/vessel-openai-api-v1/chatCompletion"
    # url = get_model + "/streaming/completion"
    utc = pytz.utc
    now = datetime.datetime.now(utc)
    current_time = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ[UTC]")
    request_time = current_time
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": bearer_token,
    }
    completion_payload = json.dumps(
        {
            "prompt": "where is the headquarter of Pfizer in india",
            "engine": "gpt-4-32k",
            "max_tokens": 4000,
            "temperature": 0,
            "stream": True,
        }
    )

    try:
        request_ = client.build_request(
            "POST", url, headers=headers, data=completion_payload
        )
        response = await client.send(request_, stream=True)
        final_text = ""
        engine = "gpt-4-32k"
        if engine == "gpt-35-turbo":
            engine = "gpt-3.5-turbo"
        total_tokens = calculate_token_count("where is the headquarter of Pfizer in india", engine)
        chunk_list = []
        final_text = ""
        if response.status_code == 200:
            chunk_list = []
            # iterate for chunks one by one
            async for chunk in response.aiter_lines():
                if chunk:
                    data = chunk.split("data:")[1]
                    if data != " [DONE]":
                        response_data = json.loads(data)
                        if response_data["choices"][0]["finish_reason"] is None:
                            if "text" in response_data["choices"][0]:
                                stream_start = True
                                content_str = response_data["choices"][0]["text"]
                                total_tokens = total_tokens + calculate_token_count(
                                    content_str, engine
                                )
                                res = {"token_count": total_tokens, "text": content_str}
                                chunk_list.append(content_str)
                                eos = False
                                stream_obj = json.dumps(
                                    {
                                        "status_code": 200,
                                        "status": "success",
                                        "data": res,
                                        "eos": eos,
                                    }
                                )
                                yield (f"data: {stream_obj}\n\n")
                            else:
                                logger.error(
                                    f"Incomplete data in chunk from vessel", data
                                )

                        if (
                            response_data["choices"][0]["finish_reason"] == "stop"
                            or response_data["choices"][0]["finish_reason"]
                        ):
                            final_text = "".join(chunk_list)
                            stream_start = True
                            eos = True
                            res = {"token_count": total_tokens, "text": final_text}
                            stream_obj = json.dumps(
                                {
                                    "status_code": 200,
                                    "status": "success",
                                    "data": res,
                                    "eos": eos,
                                }
                            )
                            yield (f"data: {stream_obj}\n\n")
        else:
            logger.error(f"Error while receiving chunks from vessel")
            raise HTTPException(status_code=400, detail="Internal Vessel Error")

    except Exception as e:
        logger.error(f"Exception in stream_completion function: {str(e)}")
        raise e

    finally:
        if stream_start:
            final_text = "".join(chunk_list)
            vessel_response = {
                "status": "success",
                "result": final_text,
                "totalTokens": total_tokens,
            }
            vessel_response = json.dumps(vessel_response)
            input_request.scope["openai_resp"] = vessel_response
            input_request.scope["user_data"] = user_data
            input_request.scope["model_used"] = request.dict().get(
                "engine", "no_engine"
            )

# Function to consume the async generator
async def consume_stream():
    async for data in stream_completion(client, input_request=None, user_data=None):
        print(data)

# Create an AsyncClient instance
client = AsyncClient()

# Call the function in the notebook
await consume_stream()

# Close the AsyncClient instance
await client.aclose()
