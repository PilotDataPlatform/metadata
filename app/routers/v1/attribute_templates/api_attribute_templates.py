from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv

from app.models.base_models import EAPIResponseCode
from app.models.models_attribute_templates import DELETETemplate
from app.models.models_attribute_templates import DELETETemplateResponse
from app.models.models_attribute_templates import GETTemplate
from app.models.models_attribute_templates import GETTemplateResponse
from app.models.models_attribute_templates import POSTTemplate
from app.models.models_attribute_templates import POSTTemplateResponse
from app.models.models_attribute_templates import PUTTemplate
from app.models.models_attribute_templates import PUTTemplateResponse
from app.routers.router_utils import set_api_response_error

from .crud import create_template
from .crud import delete_template_by_id

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

    @router.delete('/', response_model=DELETETemplateResponse, summary='Delete an attribute template')
    async def delete_attribute_template(self, params: DELETETemplate = Depends(DELETETemplate)):
        try:
            api_response = DELETETemplateResponse()
            delete_template_by_id(params, api_response)
        except Exception:
            set_api_response_error(api_response, 'Failed to delete template', EAPIResponseCode.bad_request)
        return api_response.json_response()
