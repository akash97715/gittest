import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import tiktoken
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
IAS_OPENAI_URL = "https://mule4api-comm-amer-stg.pfizer.com/vessel-openai-api-v1/completion"
IAS_OPENAI_CHAT_URL = "https://mule4api-comm-amer-stg.pfizer.com/vessel-openai-api-v1/chatCompletion"
PINGFEDERATE_URL = "https://stgfederate.pfizer.com/as/token.oauth2?grant_type=client_credentials"
IAS_EMBEDDINGS_URL = "https://mule4api-comm-amer-stg.pfizer.com/vessel-openai-api-v1/embeddings"
EMBEDDING_MODEL = "text-embedding-ada-002"
LLM_MODEL = "gpt-4"
VECTOR_INDEX = ""
CLIENT_ID = "d424daac767d4b76882b6d1a11b941cb"
CLIENT_SECRET = "4a980D3E80224DC488DFEdeB783C2154"
S3_BUCKET = "vox-usecase-biopharma"
DOC_INS_BASE = "https://mule4api-comm-amer-stg.pfizer.com/vessel-docinsight-api-v1"
DOC_INS_INGEST = f"{DOC_INS_BASE}/ingest"
DOC_INS_SEARCH = f"{DOC_INS_BASE}/search"
DOC_INS_STATUS = f"{DOC_INS_BASE}/status"

def federate_auth() -> str:
    """Obtains auth access token for accessing GPT endpoints"""
    try:
        payload = f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(PINGFEDERATE_URL, headers=headers, data=payload)
        response.raise_for_status()
        token = response.json()["access_token"]
        logger.info("Successfully obtained access token")
        return token
    except requests.exceptions.HTTPError as e:
        logger.error("HTTP Error: %s", e)
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection Error: %s", e)
    except requests.exceptions.Timeout as e:
        logger.error("Timeout Error: %s", e)
    except requests.exceptions.RequestException as e:
        logger.error("Request Error: %s", e)

def fetch_answer_from_chat_completion(user_query, instr, md5, file_name=None, vector_score_threshold=0.6, num_of_citations=5, max_tokens=4000):
    payload = json.dumps({
        "engine": LLM_MODEL,
        "messages": [
            {"role": "system", "content": instr},
            {"role": "user", "content": user_query},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
    })

    token = federate_auth()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    retries = 4
    while retries > 0:
        logger.info("Fetching chat completion (attempt %d)", 5 - retries)
        response = requests.post(IAS_OPENAI_CHAT_URL, headers=headers, data=payload)
        if response.status_code == 200 and response.json().get("result"):
            logger.info("Successfully fetched chat completion")
            return json.loads(response.json()["result"])["content"]
        retries -= 1
        logger.warning("Failed to fetch chat completion, retrying...")

    logger.error("Failed to fetch chat completion after retries")
    return "something went wrong! Try again after sometime."

def count_token(text: str, model_name: str = "gpt-4"):
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))

def process_batch(batch_number, total_prompts, user_query, instr, md5, vector_score_threshold, num_of_citations, max_tokens):
    logger.info("Processing batch %d", batch_number)
    with ThreadPoolExecutor(max_workers=total_prompts) as executor:
        futures = [executor.submit(fetch_answer_from_chat_completion, user_query, instr, md5, None, vector_score_threshold, num_of_citations, max_tokens) for _ in range(total_prompts)]
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    return results

def main(total_prompts, total_batches):
    user_query = """Provide the results of the study. For each score, include all the information related to the dosages of treatments and the percentages of patients.
                    Provide all details of patients who were selected in the study. Include the details of side effects, efficacy, and endpoints. """
    instr = """Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words."""
    md5 = "your_md5_value"  # replace with actual md5 value
    vector_score_threshold = 0.6
    num_of_citations = 5
    max_tokens = 4000

    for batch_number in range(total_batches):
        results = process_batch(batch_number, total_prompts, user_query, instr, md5, vector_score_threshold, num_of_citations, max_tokens)
        for result in results:
            if isinstance(result, str):
                logger.error("Error: %s", result)
            else:
                answer = result
                response_token_cnt = count_token(answer)
                user_question_token = count_token(user_query)
                instr_token = count_token(instr)
                logger.info(f"response_token_cnt - {response_token_cnt} \n user_question_token - {user_question_token}  \n instr_token - {instr_token}")

if __name__ == "__main__":
    total_prompts = 5  # Number of prompts per batch
    total_batches = 3  # Number of sequential batches
    main(total_prompts, total_batches)
