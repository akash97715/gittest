async def fetch_content_from_uuids(uuids: List[str]):
    content_list = []
   
    content = docstore.mmget(uuids)
    if content is None:
        raise HTTPException(
            status_code=404,
            detail=f"Content not found for UUID: {content}"
        )
    print("CONRENT IS",content)
   
    return what?
