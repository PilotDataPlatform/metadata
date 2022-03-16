from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from .base_models import APIResponse


# POST
class POSTItem(BaseModel):
    parent: UUID
    path: str
    type: str
    zone: int
    name: str
    size: int
    owner: str
    container: UUID
    container_type: str

class POSTItemResponse(APIResponse):
    pass
