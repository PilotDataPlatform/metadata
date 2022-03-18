from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi_sqlalchemy import db
from fastapi_utils.cbv import cbv
from sqlalchemy_utils import Ltree

from app.models.base_models import EAPIResponseCode
from app.models.models_items import GETItem
from app.models.models_items import GETItemResponse
from app.models.models_items import POSTItem
from app.models.models_items import POSTItemResponse
from app.models.sql_extended import ExtendedModel
from app.models.sql_items import ItemModel
from app.models.sql_storage import StorageModel
from app.routers.router_exceptions import BadRequestException
from app.routers.router_utils import paginate

router = APIRouter()


def combine_item_tables(item_result):
    item_data = item_result[0].to_dict()
    storage_data = item_result[1].to_dict()
    storage_data.pop('item_id')
    extended_data = item_result[2].to_dict()
    extended_data.pop('item_id')
    item_data['storage'] = storage_data
    item_data['extended'] = extended_data
    return item_data


def get_item_by_id(params, api_response):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id == params.id)
    )
    item_result = item_query.first()
    if item_result:
        api_response.total = 1
        api_response.num_of_pages = 1
        api_response.result = combine_item_tables(item_result)


def get_items_by_location(params, api_response):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.container == params.container, ItemModel.zone == params.zone)
    )
    if params.path:
        item_query = item_query.filter(ItemModel.path == params.path)
    paginate(params, api_response, item_query, combine_item_tables)


@cbv(router)
class APIItems:
    @router.get('/', response_model=GETItemResponse, summary='Get one or more items or check if an item exists')
    async def get_items(self, params: GETItem = Depends(GETItem)):
        try:
            api_response = GETItemResponse()
            if params.id:
                get_item_by_id(params, api_response)
            else:
                if not params.container or params.zone == None:
                    raise BadRequestException('container and zone are required when getting by location')
                get_items_by_location(params, api_response)
        except BadRequestException as e:
            api_response.set_error_msg(str(e))
            api_response.set_code(EAPIResponseCode.bad_request)
        except Exception:
            api_response.set_error_msg('Failed to get item')
            api_response.set_code(EAPIResponseCode.bad_request)
        return api_response.json_response()

    @router.post('/', response_model=POSTItemResponse, summary='Create a new item')
    async def create_item(self, data: POSTItem):
        try:
            api_response = POSTItemResponse()
            if data.type not in ['file', 'folder']:
                raise BadRequestException('type must be file or folder')
            if data.container_type not in ['project', 'dataset']:
                raise BadRequestException('container_type must be project or dataset')
            item_model_data = {
                'parent': data.parent,
                'path': Ltree(data.path),
                'type': data.type,
                'zone': data.zone,
                'name': data.name,
                'size': data.size,
                'owner': data.owner,
                'container': data.container,
                'container_type': data.container_type,
            }
            item = ItemModel(**item_model_data)
            storage_model_data = {
                'item_id': item.id,
                'location_uri': data.location_uri,
                'version': data.version,
            }
            storage = StorageModel(**storage_model_data)
            extended_model_data = {
                'item_id': item.id,
                'extra': {},
            }
            extended = ExtendedModel(**extended_model_data)
            db.session.add(item)
            db.session.add(storage)
            db.session.add(extended)
            db.session.commit()
            db.session.refresh(item)
            db.session.refresh(storage)
            db.session.refresh(extended)
            api_response.result = item.to_dict()
        except BadRequestException as e:
            api_response.set_error_msg(str(e))
            api_response.set_code(EAPIResponseCode.bad_request)
        except Exception:
            api_response.set_error_msg('Failed to create item')
            api_response.set_code(EAPIResponseCode.bad_request)
        return api_response.json_response()

    @router.put('/', summary='Update an item')
    async def update_item(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.patch('/', summary='Move an item to the trash')
    async def trash_item(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.delete('/', summary='Permanently delete an item')
    async def delete_item(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)
