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
from app.models.models_collections import DELETECollectionItems
from app.models.models_collections import DELETECollectionItemsResponse
from app.models.models_collections import DELETECollectionResponse
from app.models.models_collections import GETCollection
from app.models.models_collections import GETCollectionItems
from app.models.models_collections import GETCollectionItemsResponse
from app.models.models_collections import GETCollectionResponse
from app.models.models_collections import POSTCollection
from app.models.models_collections import POSTCollectionItems
from app.models.models_collections import POSTCollectionItemsResponse
from app.models.models_collections import POSTCollectionResponse
from app.models.models_collections import PUTCollectionResponse
from app.models.models_collections import PUTCollections
from app.routers.router_exceptions import BadRequestException
from app.routers.router_utils import set_api_response_error

from .crud import add_items
from .crud import create_collection
from .crud import get_items_per_collection
from .crud import get_user_collections
from .crud import remove_collection
from .crud import remove_items
from .crud import update_collection

router = APIRouter()
router_bulk = APIRouter()
_logger = LoggerFactory('api_collections').get_logger()


@cbv(router)
class APICollections:
    @router.get('/', response_model=GETCollectionResponse, summary='Get collections that belong to a user per project')
    async def get_collections(self, params: GETCollection = Depends(GETCollection)):
        try:
            api_response = GETCollectionResponse()
            get_user_collections(params, api_response)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response,
                                   f'Failed to get collections:user {params.owner}; project {params.container_code}',
                                   EAPIResponseCode.not_found)
        return api_response.json_response()

    @router.post('/', response_model=POSTCollectionResponse,
                 summary='Create a collection')
    async def create_new_collection(self, data: POSTCollection):
        try:
            api_response = POSTCollectionResponse()
            create_collection(data, api_response)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, f'Failed to create collection with id {data.id}',
                                   EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.get('/items/', response_model=GETCollectionItemsResponse,
                summary='Get items that belong to a collection')
    async def get_collection_items(self, params: GETCollectionItems = Depends(GETCollectionItems)):
        try:
            api_response = GETCollectionItemsResponse()
            get_items_per_collection(params, api_response)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, f'Failed to get items from collection {params.id}',
                                   EAPIResponseCode.not_found)
        return api_response.json_response()

    @router.put('/', response_model=PUTCollectionResponse,
                summary='Update a collection(s) name')
    async def update_collection_name(self, data: PUTCollections):
        try:
            api_response = PUTCollectionResponse()
            update_collection(data, api_response)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, 'Failed to update collection(s)',
                                   EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.delete('/', response_model=DELETECollectionResponse,
                   summary='Delete a collection')
    async def remove_collection(self, id: UUID):
        try:
            api_response = DELETECollectionResponse()
            remove_collection(id)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, f'Failed to delete collection {id}',
                                   EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.post('/items/', response_model=POSTCollectionItemsResponse,
                 summary='Add items to a collection')
    async def add_items_to_collection(self, data: POSTCollectionItems):
        try:
            api_response = POSTCollectionItemsResponse()
            add_items(data, api_response)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, f'Failed to add items to collection {id}',
                                   EAPIResponseCode.internal_error)
        return api_response.json_response()

    @router.delete('/items/', response_model=DELETECollectionItemsResponse,
                   summary='Remove items from a collection')
    async def remove_items_from_collection(self, data: DELETECollectionItems):
        try:
            api_response = DELETECollectionItemsResponse()
            remove_items(data)
        except BadRequestException as e:
            set_api_response_error(api_response, str(e), EAPIResponseCode.bad_request)
        except Exception as e:
            _logger.exception(e)
            set_api_response_error(api_response, f'Failed to delete items from collection {id}',
                                   EAPIResponseCode.internal_error)
        return api_response.json_response()
