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

from typing import List
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from .base_models import APIResponse


class GETTemplate(BaseModel):
    id: UUID


class GETTemplates(BaseModel):
    project_id: UUID
    page_size: int = 10
    page: int = 0


class GETTemplateResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'id': '85465212-168a-4f0c-a7aa-f3a19795d2ff',
            'name': 'template_name',
            'project_id': '28c608ac-1693-4318-a1c4-412caf2cd74a',
            'attributes': [
                {
                    'name': 'attribute_1',
                    'optional': True,
                    'type': 'text',
                },
                {
                    'name': 'attribute_2',
                    'optional': True,
                    'type': 'multiple_choice',
                    'value': 'val1, val2',
                },
            ],
        },
    )


class POSTTemplateAttributes(BaseModel):
    name: str
    optional: bool = True
    type: str = 'text'
    value: str

    @validator('type')
    def type_validation(cls, v):
        if v not in ['text', 'multiple_choice']:
            raise ValueError('type must be text or multiple_choice')
        return v


class POSTTemplate(BaseModel):
    name: str
    project_id: UUID
    attributes: List[POSTTemplateAttributes]


class POSTTemplateResponse(GETTemplateResponse):
    pass


class PUTTemplate(POSTTemplate):
    pass


class PUTTemplateResponse(GETTemplateResponse):
    pass


class DELETETemplate(BaseModel):
    id: UUID


class DELETETemplateResponse(APIResponse):
    pass
