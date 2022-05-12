# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from .base_models import APIResponse
from .base_models import PaginationRequest


class Collection(BaseModel):
    id: UUID
    name: str


class GETCollection(PaginationRequest):
    owner: str
    container_code: str


class GETCollectionID(BaseModel):
    id: UUID


class GETCollectionItems(PaginationRequest):
    id: UUID
    archived: bool = False


class GETCollectionResponse(APIResponse):
    result: list = Field(
        {},
        example=[{
            'id': '52c4a134-8550-4acc-9ab9-596548c91c52',
            'name': 'collection1',
            'owner': 'admin',
            'container_code': 'project123',
            'created_time': '2022-04-13 13:30:10.890347',
            'last_updated_time': '2022-04-13 13:30:10.890347'
        }],
    )


class GETCollectionItemsResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'id': '85465212-168a-4f0c-a7aa-f3a19795d2ff',
            'parent': '28c608ac-1693-4318-a1c4-412caf2cd74a',
            'parent_path': 'path.to.file',
            'type': 'file',
            'zone': 0,
            'name': 'filename',
            'size': 0,
            'owner': 'username',
            'container_code': 'project_code',
            'container_type': 'project',
            'created_time': '2022-04-13 13:30:10.890347',
            'last_updated_time': '2022-04-13 13:30:10.890347',
            'storage': {
                'id': 'ba623005-8183-419a-972a-e4ce0d539349',
                'location_uri': 'https://example.com/item',
                'version': '1.0',
            },
            'extended': {
                'id': 'dc763d28-7e74-4db3-a702-fa719aa702c6',
                'extra': {
                    'tags': ['tag1', 'tag2'],
                    'system_tags': ['tag1', 'tag2'],
                    'attributes': {'101778d7-a628-41ea-823b-e4b377f3476c': {'key1': 'value1', 'key2': 'value2'}},
                },
            },
        },
    )


class POSTCollection(BaseModel):
    id: Optional[UUID] = Field(example='3fa85f64-5717-4562-b3fc-2c963f66afa6')
    owner: str
    container_code: str
    name: str

    class Config:
        anystr_strip_whitespace = True


class POSTCollectionResponse(GETCollectionResponse):
    pass


class PUTCollections(BaseModel):
    owner: str
    container_code: str
    collections: list[Collection]

    @validator('collections')
    def check_duplicate_collection_names(cls, v):
        names = [collection.name for collection in v]
        if len(names) is not len(set(names)):
            raise ValueError('Cannot use duplicate collection names')
        return v


class PUTCollectionResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'owner': 'admin',
            'container_code': 'project123',
            'collections': [{'id': '52c4a134-8550-4acc-9ab9-596548c91c52', 'name': 'collection2'}]
        },
    )


class POSTCollectionItems(BaseModel):
    id: UUID
    item_ids: list[UUID]


class POSTCollectionItemsResponse(APIResponse):
    result: list = Field(
        [],
        example=['3b3aad9e-2a39-4153-8146-87fb0923bab8', '95f1c2ac-dd77-43b4-af53-2ce8f901ff78'],
    )


class DELETECollectionResponse(APIResponse):
    pass


class DELETECollectionItems(BaseModel):
    id: UUID
    item_ids: list[UUID]


class DELETECollectionItemsResponse(APIResponse):
    pass
