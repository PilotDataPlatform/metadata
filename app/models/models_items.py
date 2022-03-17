from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from .base_models import APIResponse


class GETItem(BaseModel):
    id: Optional[UUID]
    container: Optional[UUID]
    zone: Optional[int]
    path: Optional[str]
    page_size: int = 10
    page: int = 0


class GETItemResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'id': '85465212-168a-4f0c-a7aa-f3a19795d2ff',
            'parent': '28c608ac-1693-4318-a1c4-412caf2cd74a',
            'path': 'path.to.file',
            'type': 'file',
            'zone': 0,
            'name': 'filename',
            'size': 0,
            'owner': 'username',
            'container': '3789e66f-2e70-4c36-9706-473777f0fe2a',
            'container_type': 'project',
        },
    )


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


class POSTItemResponse(GETItemResponse):
    pass
