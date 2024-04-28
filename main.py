from pydantic import BaseModel, Field
from typing import List, Optional

class FetchContentRequest(BaseModel):
    uuids: Optional[List[str]] = Field(
        default=None,
        description="A list of UUIDs to fetch content for."
    )
    content_type: Optional[str] = Field(
        default=None,
        description="Type of content to fetch: 'tables', 'images', or 'both'."
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID associated with the content type."
    )
