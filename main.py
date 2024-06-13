curl --location '
https://vsl-dev.pfizer.com/openai/streaming/chatCompletion'
\
--header 'x-agw-client_id: 6f90ab7409494cdfb67e09de2de63334' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer 0001sJL7jrAi5IcKnoOEP2p3LYsT' \
--data '{
    "engine": "gpt-4-32k",
    "messages": [
        {
            "role": "assistant",
            "content": "You are a digital assistant for Pfizer Inc."
        },
        {
            "role": "user",
            "content": "Where does Pfizer Main branch located in India?"
        }
    ],
    "temperature": 0,
    "max_tokens": 100,
    "n": 1,
    "stop": ".",
    "logit_bias": {
        "2435": -100
    },
    "frequency_penalty": 0,
    "presence_penalty": 0
}'
