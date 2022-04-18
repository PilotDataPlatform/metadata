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


class GETItem(BaseModel):
    id: UUID


class GETItemsByIDs(BaseModel):
    page_size: int = 10
    page: int = 0


class GETItemsByLocation(BaseModel):
    container_code: str
    zone: int
    recursive: bool
    archived: bool = False
    parent_path: Optional[str]
    name: Optional[str]
    page_size: int = 10
    page: int = 0


class GETItemResponse(APIResponse):
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


class POSTItem(BaseModel):
    parent: UUID
    parent_path: Optional[str]
    type: str = 'file'
    zone: int = 0
    name: str
    size: int
    owner: str
    container_code: str
    container_type: str = 'project'
    location_uri: str
    version: str
    tags: list[str] = []
    system_tags: list[str] = []
    attribute_template_id: Optional[UUID]
    attributes: dict = {}

    @validator('type')
    def type_validation(cls, v):
        if v not in ['file', 'folder']:
            raise ValueError('type must be file or folder')
        return v

    @validator('container_type')
    def container_type_validation(cls, v):
        if v not in ['project', 'dataset']:
            raise ValueError('container_type must be project or dataset')
        return v

    @validator('tags')
    def tags_count(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum of 10 tags')
        return v
    
    @validator('system_tags')
    def system_tags_count(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum of 10 system tags')
        return v

    @validator('name')
    def folder_name_validation(cls, v, values):
        if 'type' in values and values['type'] == 'folder' and '.' in v:
            raise ValueError('Folder name cannot contain reserved character .')
        return v


class POSTItems(BaseModel):
    items: list[POSTItem]


class PATCHItem(BaseModel):
    id: UUID
    archived: bool


class PATCHItemResponse(GETItemResponse):
    pass


class POSTItemResponse(GETItemResponse):
    pass


class PUTItem(POSTItem):
    pass


class PUTItems(BaseModel):
    items: list[PUTItem]


class PUTItemResponse(GETItemResponse):
    pass


class DELETEItem(BaseModel):
    id: UUID


class DELETEItemResponse(APIResponse):
    pass
