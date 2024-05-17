
## fetch chunks from doc-insight
def fetch_doc_chunks(user_query, md5, file_name=None, vector_score_threshold=0.6, num_of_citations=5, max_tokens=4000):
    if md5:
        metadata = {
          'label': 'biopharma',
           'category': 'APLS',
           # 'filename': 'AE article.pdf',
           'md5': md5
        }
    else:
        metadata = {
          'label': 'biopharma',
           'category': 'APLS',
           'filename': file_name,
           # 'md5': md5
        }
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
      # "filter": "post",
      "num_of_citations": num_of_citations
    })
 
    token = federate_auth()
 
    headers = {
      'Content-Type': 'application/json',
      "Authorization": f"Bearer {token}",
    }
    print(f"payload: {req_payload}")
    response = requests.post(url=DOC_INS_SEARCH, data=req_payload, headers=headers)
    cit_chunks = response.json()
    # print(f"context chunks: {cit_chunks}")
    ctx_lst = [x.get('text') or x.get('page_content') for x in cit_chunks.get('citation')]
    # print(f"context list: {ctx_lst}")
    ctx_str = "\n\n".join(ctx_lst)
    return ctx_str, ctx_lst
 
## call chat completion API with the extracted chunks
def fetch_answer_from_chat_completion(user_query, instr, md5, file_name=None, vector_score_threshold=0.6, num_of_citations=5, max_tokens=4000):
    ctx_str, ctx_lst = fetch_doc_chunks(user_query, md5, file_name, vector_score_threshold, num_of_citations, max_tokens)
    # print(ctx_str)
    payload = json.dumps(
                {
                    "engine": LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": instr},
                        {"role": "user", "content": user_query},
                        {"role": "user", "content": ctx_str},
                    ],
                    "temperature": 0,
                    "max_tokens": max_tokens,
                }
            )
    token = federate_auth()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
 
    }
    response = requests.post(IAS_OPENAI_CHAT_URL, headers=headers, data=payload)
    # print(response.json())
   
    if response.json().get("result"):
        # print(f"context list: {ctx_lst}")
        return json.loads(response.json()["result"])["content"], ctx_lst
    else:
        print(response.text)
        return "something went wrong! Try again after sometime."

def count_token(text: str, model_name: str = "gpt-4"):
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))

## ask question
for i in range(5):
    print(f"execution sequence - {i}")
    user_query = """Provide the results of the study. For each score, include all the information related to the dosages of treatments and the percentages of patients.
                    Provide all details of patients who were selected in teh study. Include the details of side effects, efficacy, and endpoints. """
    instr = """Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words.
                Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words.
                Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words.
                Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words.
                Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words.
                Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words.
                Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words.
                Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words.
                Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words.
                Pretend that you are a researcher who needs to answer in scholar tone.
                You are writing a detailed article related to the study. The article can be successfully published only if it has more than 1500 words"""
 
    result = fetch_answer_from_chat_completion(user_query, instr, md5, None, vector_score_threshold, num_of_citations, max_tokens)
 
    if isinstance(result, str):
        print(result)
    else:
        answer, citations = result
        response_token_cnt = count_token(answer)
        user_question_token = count_token(user_query)
        instr_token = count_token(instr)
        citation_token = count_token("".join(citations))
 
    print(f"response_token_cnt - {response_token_cnt} \n user_question_token - {user_question_token}  \n instr_token - {instr_token} \n citation_token - {citation_token} \n # of citations: {len(citations)}")
    # print(f"Answer: {answer}")
    # print(f"Context: {citations}")
    # print(f"# of citations: {len(citations)}")
