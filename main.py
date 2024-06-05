curl --location '
https://mule4api-comm-amer-dev.pfizer.com/vessel-docinsight-api-v1/search'
\
--header 'x_agw_request_time: 2023-10-09T09:13:52.405Z[UTC]' \
--header 'x_agw_api_id: 18997576' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer 0001vbxb5RewQrgpFWgJ51L9kTri' \
--data '{
    "user_query": "what is there in document",
    "context": [],
    "embedding_engine": "text-embedding-ada-002",
    "llm_engine": "gpt-4-32k",
    "llm_response_flag": false,
    "temperature": 0,
    "max_tokens": 14000,
    "metadata": {
        "documentmd5": [
            "64e82e244f1f558a1ab96835b297f303"
        ]
    },
    "with_score": true,

    "num_of_citations": 1000
}'
