from typing import List
from fastapi import HTTPException

async def fetch_content_from_uuids(uuids: List[str]):
    # Fetch content from the document store using a multi-get operation
    content_list = docstore.mmget(uuids)

    # Check if the content list is empty or contains any None values (indicating missing content for some UUIDs)
    if not content_list or any(c is None for c in content_list):
        # Optionally, identify which UUIDs were not found
        missing_uuids = [uuid for uuid, content in zip(uuids, content_list) if content is None]
        raise HTTPException(
            status_code=404,
            detail=f"Content not found for UUIDs: {missing_uuids}"
        )

    # Logging the content for debugging purposes
    print("CONTENT IS", content_list)

    # Return a list of dictionaries mapping each UUID to its corresponding content
    return [{"uuid": uuid, "actual_content": content} for uuid, content in zip(uuids, content_list)]
