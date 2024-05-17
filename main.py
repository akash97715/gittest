import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import tiktoken

DOC_INS_SEARCH = "your_doc_ins_search_url"
IAS_OPENAI_CHAT_URL = "your_openai_chat_url"
LLM_MODEL = "your_llm_model_name"

def federate_auth():
    # Implement your authentication mechanism
    return "your_token"

def fetch_doc_chunks(user_query, md5, file_name=None, vector_score_threshold=0.6, num_of_citations=5, max_tokens=4000):
    metadata = {
        'label': 'biopharma',
        'category': 'APLS',
    }
    if md5:
        metadata['md5'] = md5
    else:
        metadata['filename'] = file_name

    req_payload = json.dumps({
        "user_query": user_query,
        "context": [],
        "embedding_engine": "text-embedding-ada-002",
        "llm_engine": LLM_MODEL,
        "llm_response_flag": False,
        "temperature": 0,
        "max_tokens": max_tokens,
        "metadata": {
            "metadata": metadata,
            "documentmd5": [md5],
        },
        "with_score": True,
        "vector_score_threshold": vector_score_threshold,
        "num_of_citations": num_of_citations
    })

    token = federate_auth()
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}",
    }

    response = requests.post(url=DOC_INS_SEARCH, data=req_payload, headers=headers)
    cit_chunks = response.json()
    ctx_lst = [x.get('text') or x.get('page_content') for x in cit_chunks.get('citation')]
    ctx_str = "\n\n".join(ctx_lst)
    return ctx_str, ctx_lst

def fetch_answer_from_chat_completion(user_query, instr, md5, file_name=None, vector_score_threshold=0.6, num_of_citations=5, max_tokens=4000):
    ctx_str, ctx_lst = fetch_doc_chunks(user_query, md5, file_name, vector_score_threshold, num_of_citations, max_tokens)
    payload = json.dumps({
        "engine": LLM_MODEL,
        "messages": [
            {"role": "system", "content": instr},
            {"role": "user", "content": user_query},
            {"role": "user", "content": ctx_str},
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
        response = requests.post(IAS_OPENAI_CHAT_URL, headers=headers, data=payload)
        if response.status_code == 200 and response.json().get("result"):
            return json.loads(response.json()["result"])["content"], ctx_lst
        retries -= 1

    return "something went wrong! Try again after sometime."

def count_token(text: str, model_name: str = "gpt-4"):
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))

def process_batch(batch_number, total_prompts, user_query, instr, md5, vector_score_threshold, num_of_citations, max_tokens):
    results = []
    for _ in range(total_prompts):
        result = fetch_answer_from_chat_completion(user_query, instr, md5, None, vector_score_threshold, num_of_citations, max_tokens)
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

    with ThreadPoolExecutor(max_workers=total_batches) as executor:
        futures = [executor.submit(process_batch, i, total_prompts, user_query, instr, md5, vector_score_threshold, num_of_citations, max_tokens) for i in range(total_batches)]
        
        for future in as_completed(futures):
            try:
                results = future.result()
                for result in results:
                    if isinstance(result, str):
                        print(result)
                    else:
                        answer, citations = result
                        response_token_cnt = count_token(answer)
                        user_question_token = count_token(user_query)
                        instr_token = count_token(instr)
                        citation_token = count_token("".join(citations))
                        print(f"response_token_cnt - {response_token_cnt} \n user_question_token - {user_question_token}  \n instr_token - {instr_token} \n citation_token - {citation_token} \n # of citations: {len(citations)}")
            except Exception as e:
                print(f"Batch failed with exception: {e}")

if __name__ == "__main__":
    total_prompts = 5  # Number of prompts per batch
    total_batches = 3  # Number of parallel batches
    main(total_prompts, total_batches)
