from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv

from app.models.base_models import EAPIResponseCode
from app.models.models_attribute_templates import POSTTemplate
from app.models.models_attribute_templates import POSTTemplateResponse
from app.routers.router_exceptions import BadRequestException

from .crud import create_template

router = APIRouter()


@cbv(router)
class APIAttributeTemplates:
    @router.get('/', summary='Get an attribute template')
    async def get_attribute_template(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.post('/', response_model=POSTTemplateResponse, summary='Create a new attribute template')
    async def create_attribute_template(self, data: POSTTemplate):
        try:
            api_response = POSTTemplateResponse()
            create_template(data, api_response)
        except Exception:
            api_response.set_error_msg('Failed to create attribute template')
            api_response.set_code(EAPIResponseCode.bad_request)
        return api_response.json_response()

    @router.put('/', summary='Update an attribute template')
    async def update_attribute_template(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.delete('/', summary='Delete an attribute template')
    async def delete_attribute_template(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)
