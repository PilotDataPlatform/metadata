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

from uuid import UUID

from common import LoggerFactory
from fastapi import APIRouter
from fastapi import Depends
from fastapi_utils.cbv import cbv

from app.models.base_models import EAPIResponseCode
from app.models.models_attribute_templates import DELETETemplate
from app.models.models_attribute_templates import DELETETemplateResponse
from app.models.models_attribute_templates import GETTemplate
from app.models.models_attribute_templates import GETTemplateResponse
from app.models.models_attribute_templates import GETTemplates
from app.models.models_attribute_templates import POSTTemplate
from app.models.models_attribute_templates import POSTTemplateResponse
from app.models.models_attribute_templates import PUTTemplate
from app.models.models_attribute_templates import PUTTemplateResponse
from app.routers.router_exceptions import EntityNotFoundException
from app.routers.router_utils import set_api_response_error

from .crud import create_template
from .crud import delete_template_by_id
from .crud import get_template_by_id
from .crud import get_templates_by_project_id
from .crud import update_template

router = APIRouter()
_logger = LoggerFactory('api_attribute_templates').get_logger()


@cbv(router)
class APIAttributeTemplates:
    @router.get('/{id}/', response_model=GETTemplateResponse, summary='Get an attribute template')
    async def get_attribute_template(self, params: GETTemplate = Depends(GETTemplate)):
        try:
            api_response = GETTemplateResponse()
            get_template_by_id(params, api_response)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(
                api_response, f'Failed to get template with id {params.id}', EAPIResponseCode.not_found
            )
        return api_response.json_response()

    @router.get('/', summary='Get all attribute templates associated with a project')
    async def get_attribute_templates(self, params: GETTemplates = Depends(GETTemplates)):
        try:
            api_response = GETTemplateResponse()
            get_templates_by_project_id(params, api_response)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(
                api_response, f'Failed to get templates with project_id {params.project_id}', EAPIResponseCode.not_found
            )
        return api_response.json_response()

    @router.post('/', response_model=POSTTemplateResponse, summary='Create a new attribute template')
    async def create_attribute_template(self, data: POSTTemplate):
        try:
            api_response = POSTTemplateResponse()
            create_template(data, api_response)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to create attribute template', EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.put('/', response_model=PUTTemplateResponse, summary='Update an attribute template')
    async def update_attribute_template(self, id: UUID, data: PUTTemplate):
        try:
            api_response = PUTTemplateResponse()
            update_template(id, data, api_response)
        except EntityNotFoundException:
            set_api_response_error(api_response, f'Failed to get template with id {id}', EAPIResponseCode.not_found)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to update attribute template', EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.delete('/', response_model=DELETETemplateResponse, summary='Delete an attribute template')
    async def delete_attribute_template(self, params: DELETETemplate = Depends(DELETETemplate)):
        try:
            api_response = DELETETemplateResponse()
            delete_template_by_id(params, api_response)
        except EntityNotFoundException:
            set_api_response_error(
                api_response, f'Failed to get template with id {params.id}', EAPIResponseCode.not_found
            )
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to delete template', EAPIResponseCode.internal_error)
        return api_response.json_response()
