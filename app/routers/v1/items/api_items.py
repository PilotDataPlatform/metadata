from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi_utils.cbv import cbv

from app.models.base_models import EAPIResponseCode
from app.models.models_items import DELETEItem
from app.models.models_items import DELETEItemResponse
from app.models.models_items import GETItem
from app.models.models_items import GETItemResponse
from app.models.models_items import PATCHItem
from app.models.models_items import PATCHItemResponse
from app.models.models_items import POSTItem
from app.models.models_items import POSTItemResponse
from app.models.models_items import PUTItem
from app.models.models_items import PUTItemResponse
from app.routers.router_exceptions import BadRequestException
from app.routers.router_utils import set_api_response_error

from .crud import archive_item_by_id
from .crud import create_item
from .crud import delete_item_by_id
from .crud import get_item_by_id
from .crud import get_items_by_location
from .crud import update_item

router = APIRouter()


@cbv(router)
class APIItems:
    @router.get('/', response_model=GETItemResponse, summary='Get one or more items or check if an item exists')
    async def get_items(self, params: GETItem = Depends(GETItem)):
        try:
            api_response = GETItemResponse()
            if params.id:
                get_item_by_id(params, api_response)
            else:
                if not params.container_code or params.zone is None or params.archived is None:
                    raise BadRequestException(
                        'container_code, zone, and archived are required when getting by location'
                    )
                get_items_by_location(params, api_response)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception:
            api_response.set_error_msg('Failed to get item')
            api_response.set_code(EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.post('/', response_model=POSTItemResponse, summary='Create a new item')
    async def create_item(self, data: POSTItem):
        try:
            api_response = POSTItemResponse()
            create_item(data, api_response)
        except Exception:
            api_response.set_error_msg('Failed to create item')
            api_response.set_code(EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.put('/', response_model=PUTItemResponse, summary='Update an item')
    async def update_item(self, id: UUID, data: PUTItem):
        try:
            api_response = PUTItemResponse()
            update_item(id, data, api_response)
        except Exception:
            api_response.set_error_msg('Failed to update item')
            api_response.set_code(EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.patch('/', response_model=PATCHItemResponse, summary='Move an item to or out of the trash')
    async def trash_item(self, params: PATCHItem = Depends(PATCHItem)):
        try:
            api_response = PATCHItemResponse()
            archive_item_by_id(params, api_response)
        except Exception:
            api_response.set_error_msg('Failed to archive item')
            api_response.set_code(EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.delete('/', response_model=DELETEItemResponse, summary='Permanently delete an item')
    async def delete_item(self, params: DELETEItem = Depends(DELETEItem)):
        try:
            api_response = DELETEItemResponse()
            delete_item_by_id(params, api_response)
        except Exception:
            api_response.set_error_msg('Failed to delete item')
            api_response.set_code(EAPIResponseCode.internal_error)
        return api_response.json_response()
