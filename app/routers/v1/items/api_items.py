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

from common import LoggerFactory
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi_utils.cbv import cbv

from app.models.base_models import EAPIResponseCode
from app.models.models_items import DELETEItem
from app.models.models_items import DELETEItemResponse
from app.models.models_items import GETItem
from app.models.models_items import GETItemResponse
from app.models.models_items import GETItemsByIDs
from app.models.models_items import GETItemsByLocation
from app.models.models_items import PATCHItem
from app.models.models_items import PATCHItemResponse
from app.models.models_items import POSTItem
from app.models.models_items import POSTItemResponse
from app.models.models_items import POSTItems
from app.models.models_items import PUTItem
from app.models.models_items import PUTItemResponse
from app.models.models_items import PUTItems
from app.models.models_items import PUTItemsBequeath
from app.models.models_items import PUTItemsBequeathResponse
from app.routers.router_exceptions import BadRequestException
from app.routers.router_exceptions import EntityNotFoundException
from app.routers.router_utils import set_api_response_error

from .crud import archive_item_by_id
from .crud import bequeath_to_children
from .crud import create_item
from .crud import create_items
from .crud import delete_item_by_id
from .crud import delete_items_by_ids
from .crud import get_item_by_id
from .crud import get_items_by_ids
from .crud import get_items_by_location
from .crud import update_item
from .crud import update_items

router = APIRouter()
router_bulk = APIRouter()
_logger = LoggerFactory('api_items').get_logger()


@cbv(router)
class APIItems:
    @router.get('/{id}/', response_model=GETItemResponse, summary='Get an item by ID or check if an item exists')
    async def get_item(self, params: GETItem = Depends(GETItem)):
        try:
            api_response = GETItemResponse()
            get_item_by_id(params, api_response)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, f'Failed to get item with id {params.id}', EAPIResponseCode.not_found)
        return api_response.json_response()

    @router.post('/', response_model=POSTItemResponse, summary='Create a new item')
    async def create_item(self, data: POSTItem):
        try:
            api_response = POSTItemResponse()
            api_response.result = create_item(data)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to create item', EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.put('/', response_model=PUTItemResponse, summary='Update an item')
    async def update_item(self, id: UUID, data: PUTItem):
        try:
            api_response = PUTItemResponse()
            api_response.result = update_item(id, data)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to update item', EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.patch('/', response_model=PATCHItemResponse, summary='Move an item to or out of the trash')
    async def trash_item(self, params: PATCHItem = Depends(PATCHItem)):
        try:
            api_response = PATCHItemResponse()
            archive_item_by_id(params, api_response)
        except EntityNotFoundException:
            set_api_response_error(api_response, f'Failed to get item with id {params.id}', EAPIResponseCode.not_found)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to archive item', EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.delete('/', response_model=DELETEItemResponse, summary='Permanently delete an item')
    async def delete_item(self, params: DELETEItem = Depends(DELETEItem)):
        try:
            api_response = DELETEItemResponse()
            delete_item_by_id(params.id, api_response)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to delete item', EAPIResponseCode.internal_error)
        return api_response.json_response()


@cbv(router_bulk)
class APIItemsBulk:
    @router_bulk.get('/batch/', response_model=GETItemResponse, summary='Get many items by IDs')
    async def get_items_by_ids(self, ids: List[UUID] = Query(None), params: GETItemsByIDs = Depends(GETItemsByIDs)):
        try:
            api_response = GETItemResponse()
            get_items_by_ids(params, ids, api_response)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to get item', EAPIResponseCode.not_found)
        return api_response.json_response()

    @router_bulk.get('/search/', response_model=GETItemResponse, summary='Get all items by location')
    async def get_items_by_location(self, params: GETItemsByLocation = Depends(GETItemsByLocation)):
        try:
            api_response = GETItemResponse()
            get_items_by_location(params, api_response)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to get item', EAPIResponseCode.not_found)
        return api_response.json_response()

    @router_bulk.post('/batch/', response_model=POSTItemResponse, summary='Create many new items')
    async def create_items(self, data: POSTItems):
        try:
            api_response = POSTItemResponse()
            create_items(data, api_response)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to create items', EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router_bulk.put('/batch/', response_model=PUTItemResponse, summary='Update many items')
    async def update_items(self, data: PUTItems, ids: List[UUID] = Query(None)):
        try:
            api_response = PUTItemResponse()
            if len(data.items) != len(ids):
                raise BadRequestException('Number of IDs does not match number of update data')
            update_items(ids, data, api_response)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to update items', EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router_bulk.delete('/batch/', response_model=DELETEItemResponse, summary='Permanently delete many items by IDs')
    async def delete_items_by_ids(self, ids: List[UUID] = Query(None)):
        try:
            api_response = DELETEItemResponse()
            delete_items_by_ids(ids, api_response)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to delete items', EAPIResponseCode.not_found)
        return api_response.json_response()

    @router_bulk.put(
        '/batch/bequeath/',
        response_model=PUTItemsBequeathResponse,
        summary='Bequeath properties to a folder\'s children',
    )
    async def update_items_bequeath(self, data: PUTItemsBequeath, id: UUID = Query(None)):
        try:
            api_response = PUTItemsBequeathResponse()
            bequeath_to_children(id, data, api_response)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, f'Failed to get item with id {id}', EAPIResponseCode.not_found)
        return api_response.json_response()
