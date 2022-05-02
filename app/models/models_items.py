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

from app.config import ConfigClass

from .base_models import APIResponse
from .base_models import PaginationRequest


class GETItem(BaseModel):
    id: UUID


class GETItemsByIDs(BaseModel):
    page_size: int = 10
    page: int = 0


class GETItemsByLocation(PaginationRequest):
    container_code: str
    zone: int
    recursive: bool
    archived: bool = False
    parent_path: Optional[str]
    name: Optional[str]

    class Config:
        anystr_strip_whitespace = True


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
    id: Optional[UUID]
    parent: Optional[UUID] = Field(example='3fa85f64-5717-4562-b3fc-2c963f66afa6')
    parent_path: Optional[str] = Field(example='path.to.file')
    type: str = 'file'
    zone: int = 0
    name: str = Field(example='file_name.txt')
    size: int
    owner: str
    container_code: str
    container_type: str = 'project'
    location_uri: str
    version: str
    tags: list[str] = []
    system_tags: list[str] = []
    attribute_template_id: Optional[UUID]
    attributes: Optional[dict] = {}

    class Config:
        anystr_strip_whitespace = True

    @validator('type')
    def type_is_valid(cls, v, values):
        if v not in ['file', 'folder', 'name_folder']:
            raise ValueError('type must be one of: file, folder, name_folder')
        elif 'parent' in values and values['parent'] and v == 'name_folder':
            raise ValueError('Name folders cannot have a parent')
        elif 'parent_path' in values and values['parent_path'] and v == 'name_folder':
            raise ValueError('Name folders cannot have a parent_path')
        elif 'parent' not in values or not values['parent'] and v != 'name_folder':
            raise ValueError('Files and folders must have a parent')
        elif 'parent_path' not in values or not values['parent_path'] and v != 'name_folder':
            raise ValueError('Files and folders must have a parent_path')
        return v

    @validator('container_type')
    def container_type_is_valid(cls, v, values):
        if v not in ['project', 'dataset']:
            raise ValueError('container_type must be project or dataset')
        elif 'type' in values and values['type'] == 'name_folder' and v != 'project':
            raise ValueError('Name folders are only allowed in projects')
        return v

    @validator('tags')
    def tags_count(cls, v):
        if len(v) > ConfigClass.MAX_TAGS:
            raise ValueError(f'Maximum of {ConfigClass.MAX_TAGS} tags')
        return v

    @validator('system_tags')
    def system_tags_count(cls, v):
        if len(v) > ConfigClass.MAX_SYSTEM_TAGS:
            raise ValueError(f'Maximum of {ConfigClass.MAX_SYSTEM_TAGS} system tags')
        return v

    @validator('name')
    def folder_name_is_valid(cls, v, values):
        if 'type' in values and values['type'] == 'folder' and '.' in v:
            raise ValueError('Folder name cannot contain reserved character: .')
        return v

    @validator('attributes')
    def attributes_are_valid(cls, v, values):
        if 'type' in values and values['type'] != 'file':
            raise ValueError('Attributes can only be applied to files')
        for attribute in v.values():
            if len(attribute) > ConfigClass.MAX_ATTRIBUTE_LENGTH:
                raise ValueError(
                    f'Attribute exceeds maximum length of {ConfigClass.MAX_ATTRIBUTE_LENGTH} characters: {attribute}'
                )
        return v

    @validator('attribute_template_id')
    def attribute_template_only_on_files(cls, v, values):
        if 'type' in values and values['type'] != 'file':
            raise ValueError('Attribute templates can only be applied to files')
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
    parent: Optional[UUID] = Field(example='3fa85f64-5717-4562-b3fc-2c963f66afa6', default='')
    parent_path: Optional[str] = Field(example='path.to.file', default='')
    type: Optional[str]
    zone: Optional[int]
    name: Optional[str] = Field(example='file_name.txt')
    size: Optional[int]
    owner: Optional[str]
    container_code: Optional[str]
    container_type: Optional[str]
    location_uri: Optional[str]
    version: Optional[str]
    tags: Optional[list[str]]
    system_tags: Optional[list[str]]
    attribute_template_id: Optional[UUID]
    attributes: Optional[dict]

    class Config:
        anystr_strip_whitespace = True


class PUTItems(BaseModel):
    items: list[PUTItem]


class PUTItemResponse(GETItemResponse):
    pass


class DELETEItem(BaseModel):
    id: UUID


class DELETEItemResponse(APIResponse):
    pass


class PUTItemsBequeath(BaseModel):
    attribute_template_id: Optional[UUID]
    attributes: Optional[dict]
    system_tags: Optional[list[str]]


class PUTItemsBequeathResponse(GETItemResponse):
    pass
