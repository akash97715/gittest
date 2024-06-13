import requests

def get_chat_completion(user_query, token):
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

    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                # Decode the line from bytes to string and print
                decoded_line = line.decode('utf-8')
                print(decoded_line)

    except requests.exceptions.ChunkedEncodingError as e:
        print(f"Chunked Encoding Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")

# Example usage
user_query = "Where does Pfizer Main branch located in India?"
token = "0001rpo98AHBj95p1AqsRrO9Mdh2"
get_chat_completion(user_query, token)
