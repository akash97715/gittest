from pydantic import BaseModel, Field
from typing import List, Optional

class UUIDsRequest(BaseModel):
    uuids: Optional[List[str]] = Field(
        default=None,
        description="A list of UUIDs to fetch content for."
    )
