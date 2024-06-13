import httpx
import json

async def get_chat_completion(user_query, token):
    url = 'https://vsl-dev.pfizer.com/openai/streaming/chatCompletion'
    headers = {
        'x-agw-client_id': '6f90ab7409494cdfb67e09de2de63334',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        "engine": "gpt-4-32k",
        "messages": [
            {
                "role": "assistant",
                "content": "You are a digital assistant for Pfizer Inc."
            },
            {
                "role": "user",
                "content": user_query
            }
        ],
        "temperature": 0,
        "max_tokens": 100,
        "n": 1,
        "stream": True,
        "stop": ".",
        "logit_bias": {
            "2435": -100
        },
        "frequency_penalty": 0,
        "presence_penalty": 0
    }

    total_tokens = 0

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data, timeout=None)
        
        if response.status_code == 200:
            chunk_list = []
            async for chunk in response.aiter_lines():
                if chunk != "":
                    data = chunk.split("data:")[1].strip()
                    if data != "[DONE]":
                        response_data = json.loads(data)
                        if response_data["choices"][0]["finish_reason"] is None:
                            if "text" in response_data["choices"][0]:
                                content_str = response_data["choices"][0]["text"]
                                total_tokens += len(content_str.split())  # Simplified token count
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
                        yield ("data: [DONE]\n\n")
                        break

# Example usage
import asyncio

user_query = "Where does Pfizer Main branch located in India?"
token = "0001rpo98AHBj95p1AqsRrO9Mdh2"

async def main():
    async for data in get_chat_completion(user_query, token):
        print(data)

asyncio.run(main())
