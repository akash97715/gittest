async def invoke_retrieval_qa(
    db,
    client_id,
    x_vsl_client_id,
    bearer_auth,
    final_index_dict,
    rw,
    request:fastapi_request,
    index_name: str
):
