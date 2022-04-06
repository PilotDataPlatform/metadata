from uuid import UUID

from fastapi_sqlalchemy import db
from sqlalchemy.sql import expression
from sqlalchemy_utils import Ltree
from sqlalchemy_utils.types.ltree import LQUERY

from app.app_utils import encode_label_for_ltree
from app.app_utils import encode_path_for_ltree
from app.models.base_models import APIResponse
from app.models.models_items import DELETEItem
from app.models.models_items import GETItem
from app.models.models_items import PATCHItem
from app.models.models_items import POSTItem
from app.models.models_items import PUTItem
from app.models.sql_extended import ExtendedModel
from app.models.sql_items import ItemModel
from app.models.sql_storage import StorageModel
from app.routers.router_utils import paginate


def combine_item_tables(item_result: tuple) -> dict:
    item_data = item_result[0].to_dict()
    storage_data = item_result[1].to_dict()
    storage_data.pop('item_id')
    extended_data = item_result[2].to_dict()
    extended_data.pop('item_id')
    item_data['storage'] = storage_data
    item_data['extended'] = extended_data
    return item_data


def get_item_by_id(params: GETItem, api_response: APIResponse):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id == params.id)
    )
    item_result = item_query.first()
    if item_result:
        api_response.result = combine_item_tables(item_result)
    else:
        api_response.total = 0
        api_response.num_of_pages = 0


def get_items_by_location(params: GETItem, api_response: APIResponse):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(
            ItemModel.container == params.container,
            ItemModel.zone == params.zone,
            ItemModel.archived == params.archived,
        )
    )
    if params.path:
        regex = f'{params.path}.*{{1}}'
        item_query = item_query.filter(ItemModel.path.lquery(expression.cast(regex, LQUERY)))
    paginate(params, api_response, item_query, combine_item_tables)


def create_item(data: POSTItem, api_response: APIResponse):
    encoded_item_name = encode_label_for_ltree(data.name)
    item_model_data = {
        'parent': data.parent,
        'path': Ltree(f'{encode_path_for_ltree(data.path)}') if data.path else None,
        'archived': False,
        'type': data.type,
        'zone': data.zone,
        'name': encoded_item_name,
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
        'extra': data.extra,
    }
    extended = ExtendedModel(**extended_model_data)
    db.session.add_all([item, storage, extended])
    db.session.commit()
    db.session.refresh(item)
    db.session.refresh(storage)
    db.session.refresh(extended)
    api_response.result = combine_item_tables((item, storage, extended))


def update_item(item_id: UUID, data: PUTItem, api_response: APIResponse):
    item = db.session.query(ItemModel).filter_by(id=item_id).first()
    encoded_item_name = encode_label_for_ltree(data.name)
    item.parent = data.parent
    item.path = Ltree(f'{encode_path_for_ltree(data.path)}') if data.path else None
    item.type = data.type
    item.zone = data.zone
    item.name = encoded_item_name
    item.size = data.size
    item.owner = data.owner
    item.container = data.container
    item.container_type = data.container_type
    storage = db.session.query(StorageModel).filter_by(item_id=item_id).first()
    storage.location_uri = data.location_uri
    storage.version = data.version
    extended = db.session.query(ExtendedModel).filter_by(item_id=item_id).first()
    extended.extra = data.extra
    db.session.commit()
    db.session.refresh(item)
    db.session.refresh(storage)
    db.session.refresh(extended)
    api_response.result = combine_item_tables((item, storage, extended))


def get_available_file_path(container: UUID, zone: int, path: Ltree, archived: bool, recursions: int = 1) -> Ltree:
    item = db.session.query(ItemModel).filter_by(container=container, zone=zone, path=path, archived=archived).first()
    if item is None:
        return path
    new_path = Ltree(f'{str(path)}_{recursions}') if '_copy' in str(path) else Ltree(f'{str(path)}_copy')
    return get_available_file_path(container, zone, new_path, archived, recursions + 1)


def archive_item_by_id(params: PATCHItem, api_response: APIResponse):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id == params.id)
    )
    item_result = item_query.first()
    item = item_result[0]
    item.archived = params.archived
    if params.archived:
        item.restore_path = item.path
        item.path = get_available_file_path(item.container, item.zone, Ltree(f'{item.name}'), True)
        item.name = str(item.path).split('.')[-1]
    else:
        item.path = get_available_file_path(item.container, item.zone, item.restore_path, False)
        item.restore_path = None
        item.name = str(item.path).split('.')[-1]
    db.session.commit()
    db.session.refresh(item)
    api_response.result = combine_item_tables(item_result)


def delete_item_by_id(params: DELETEItem, api_response: APIResponse):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id == params.id)
    )
    for row in item_query.first():
        db.session.delete(row)
    db.session.commit()
    api_response.total = 0
    api_response.num_of_pages = 0
