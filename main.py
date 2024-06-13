async for chunk in response.aiter_lines():
                # for chunk in response.iter_bytes():
                if chunk != "":
                    data = chunk.split("data:")[1]
                    if data != " [DONE]":
                        response_data = json.loads(data)
                        #print(response_data)
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
