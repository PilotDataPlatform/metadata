from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from .base_models import APIResponse


class GETTemplate(BaseModel):
    id: UUID


class GETTemplates(BaseModel):
    project_id: UUID


class GETTemplateResponse(APIResponse):
    result: dict = Field(
        {},
        example={
            'id': '85465212-168a-4f0c-a7aa-f3a19795d2ff',
            'name': 'template_name',
            'project_id': '28c608ac-1693-4318-a1c4-412caf2cd74a',
            'attributes': [
                {
                    'name': 'attribute_name',
                    'optional': True,
                    'type': 'multiple_choice',
                    'value': 'val1, val2',
                }
            ],
        },
    )


class POSTTemplate(BaseModel):
    name: str
    project_id: UUID
    attributes: dict = {}


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
