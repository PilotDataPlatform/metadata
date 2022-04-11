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
    id: Optional[UUID]
    container_code: Optional[str]
    zone: Optional[int]
    parent_path: Optional[str]
    archived: Optional[bool]
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
            'storage': {
                'id': 'ba623005-8183-419a-972a-e4ce0d539349',
                'item_id': '85465212-168a-4f0c-a7aa-f3a19795d2ff',
                'location_uri': 'https://example.com/item',
                'version': '1.0',
            },
            'extended': {
                'id': 'dc763d28-7e74-4db3-a702-fa719aa702c6',
                'item_id': '85465212-168a-4f0c-a7aa-f3a19795d2ff',
                'extra': {},
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
    extra: dict = {}

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

    @validator('name')
    def folder_name_validation(cls, v, values):
        if 'type' in values and values['type'] == 'folder' and '.' in v:
            raise ValueError('Folder name cannot contain reserved character .')
        return v


class PATCHItem(BaseModel):
    id: UUID
    archived: bool


class PATCHItemResponse(GETItemResponse):
    pass


class POSTItemResponse(GETItemResponse):
    pass


class PUTItem(POSTItem):
    pass


class PUTItemResponse(GETItemResponse):
    pass


class DELETEItem(BaseModel):
    id: UUID


class DELETEItemResponse(APIResponse):
    pass
