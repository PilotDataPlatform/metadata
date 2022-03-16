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
from app.models.sql_items import ItemsModel
from app.routers.router_exceptions import BadRequestException

router = APIRouter()


@cbv(router)
class APIItems:
    @router.get('/', response_model=GETItemResponse, summary='Get one or more items or check if an item exists')
    async def get_items(self, params: GETItem = Depends(GETItem)):
        try:
            api_response = GETItemResponse()
            item = db.session.query(ItemsModel).filter_by(id=params.id)
            api_response.page = 0
            api_response.num_of_pages = 1
            api_response.total = 1
            api_response.result = item.first().to_dict()
        except Exception:
            api_response.set_error_msg(f'Could not get item with id {params.id}')
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
            model_data = {
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
            item = ItemsModel(**model_data)
            db.session.add(item)
            db.session.commit()
            db.session.refresh(item)
            api_response.result = item.to_dict()
        except BadRequestException as e:
            api_response.set_error_msg(str(e))
            api_response.set_code(EAPIResponseCode.bad_request)
        except Exception:
            api_response.set_error_msg('Failed to write to database')
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
