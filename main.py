import pytz
import datetime
import json
from httpx import HTTPException

async def stream_completion(client, input_request, user_data):
    stream_start = False

    logger.info("Streaming completion request")
    bearer_token = '0001P1lrDr2KSLQ50S6eqjytIFZp'
    url = "http://something"
    # url = get_model + "/streaming/completion"
    utc = pytz.utc
    now = datetime.datetime.now(utc)
    # print(now)
    current_time = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ[UTC]")
    # print(current_time)
    # time=datetime.datetime.now()
    # time= str(time)
    request_time = current_time
    # print(time)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": bearer_token,
        # "x-agw-client_id": client_id,
        # "x_agw_api_id": stream_api_key,
        # "x_agw_request_time": request_time,
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
        engine = request.engine
        if request.engine == "gpt-35-turbo":
            engine = "gpt-3.5-turbo"
        total_tokens = calculate_token_count(request.prompt, engine)
        chunk_list = []
        final_text = ""
        if response.status_code == 200:
            chunk_list = []
            # iterate for chunks one by one
            async for chunk in response.aiter_lines():
                # for chunk in response.iter_bytes():
                if chunk != "":
                    data = chunk.split("data:")[1]
                    if data != " [DONE]":
                        response_data = json.loads(data)
                        # print(response_data)
                        if response_data["choices"][0]["finish_reason"] is None:
                            # chunks from Vessel should consists of text
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
                                # raise Exception("Incomplete data in chunk from vessel")

                        # Final chunk should have concatenated response
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

    # For metering and audit logging in any condition.
    finally:
        # Compose vessel response for metering and audit logging only if there was some streaming.
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

# Call the function in the notebook if needed
# await stream_completion(client, input_request, user_data)
