import requests
import backoff
from datetime import datetime

# Define the payload and headers
url = 'https://mule4api-comm-amer-dev.pfizer.com/vessel-docinsight-api-v1/search'
headers = {
    'x_agw_request_time': datetime.utcnow().isoformat() + 'Z[UTC]',
    'x_agw_api_id': '18997576',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 0001vbxb5RewQrgpFWgJ51L9kTri'
}
data = {
    "user_query": "what is there in document",
    "context": [],
    "embedding_engine": "text-embedding-ada-002",
    "llm_engine": "gpt-4-32k",
    "llm_response_flag": False,
    "temperature": 0,
    "max_tokens": 14000,
    "metadata": {
        "documentmd5": [
            "64e82e244f1f558a1ab96835b297f303"
        ]
    },
    "with_score": True,
    "num_of_citations": 1000
}

# Function to make the request with backoff
@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
def make_request():
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Raise an exception for HTTP error codes
    return response.json()

def hit_endpoint(num_attempts, max_retries):
    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=max_retries)
    def request_with_retries():
        return make_request()

    results = []
    for _ in range(num_attempts):
        try:
            result = request_with_retries()
            results.append(result)
        except requests.exceptions.RequestException as e:
            print(f"Request failed after {max_retries} retries: {e}")
    
    return results

# Configure the number of attempts and retries
num_attempts = 20
max_retries = 3

# Hit the endpoint
results = hit_endpoint(num_attempts, max_retries)
for i, result in enumerate(results):
    print(f"Result {i+1}: {result}")
