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

from datetime import datetime
from uuid import UUID

from fastapi_sqlalchemy import db
from sqlalchemy.sql import expression
from sqlalchemy_utils import Ltree
from sqlalchemy_utils.types.ltree import LQUERY

from app.app_utils import decode_label_from_ltree
from app.app_utils import encode_label_for_ltree
from app.app_utils import encode_path_for_ltree
from app.models.base_models import APIResponse
from app.models.models_items import GETItem
from app.models.models_items import PATCHItem
from app.models.models_items import POSTItem
from app.models.models_items import POSTItems
from app.models.models_items import PUTItem
from app.models.models_items import PUTItems
from app.models.sql_attribute_templates import AttributeTemplateModel
from app.models.sql_extended import ExtendedModel
from app.models.sql_items import ItemModel
from app.models.sql_storage import StorageModel
from app.routers.router_exceptions import BadRequestException
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


def get_available_file_name(
    container_code: UUID,
    zone: int,
    encoded_item_name: str,
    encoded_item_path: Ltree,
    archived: bool,
    recursions: int = 1,
) -> str:
    item = (
        db.session.query(ItemModel)
        .filter_by(
            container_code=container_code,
            zone=zone,
            name=encoded_item_name,
            parent_path=encoded_item_path,
            archived=archived,
        )
        .first()
    )
    if item is None:
        return encoded_item_name
    decoded_item_name = decode_label_from_ltree(encoded_item_name)
    decoded_new_name = (
        f'{decoded_item_name}_{recursions}' if '_copy' in decoded_item_name else f'{decoded_item_name}_copy'
    )
    return get_available_file_name(
        container_code, zone, encode_label_for_ltree(decoded_new_name), encoded_item_path, archived, recursions + 1
    )


def attributes_match_template(attributes: dict, template_id: UUID) -> bool:
    if attributes == {} and not template_id:
        return True
    try:
        attribute_template = db.session.query(AttributeTemplateModel).filter_by(id=template_id).first().to_dict()
        if len(attributes) > len(attribute_template['attributes']):
            return False
        for format in attribute_template['attributes']:
            if not format['optional']:
                input_value = attributes[format['name']]
                if 'options' in format:
                    if format['options']:
                        if input_value not in format['options']:
                            return False
        return True
    except Exception:
        return False


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


def get_items_by_ids(params: GETItem, ids: list[UUID], api_response: APIResponse):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id.in_(ids))
    )
    paginate(params, api_response, item_query, combine_item_tables)


def get_items_by_location(params: GETItem, api_response: APIResponse):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(
            ItemModel.container_code == params.container_code,
            ItemModel.zone == params.zone,
            ItemModel.archived == params.archived,
        )
    )
    if params.name:
        item_query = item_query.filter(ItemModel.name == encode_label_for_ltree(params.name))
    if params.parent_path:
        regex = f'{encode_path_for_ltree(params.parent_path)}'
        if params.recursive:
            regex += '.*'
        item_query = item_query.filter(ItemModel.parent_path.lquery(expression.cast(regex, LQUERY)))
    else:
        if not params.recursive:
            item_query = item_query.filter(ItemModel.parent_path == None)
    paginate(params, api_response, item_query, combine_item_tables)


def create_item(data: POSTItem) -> dict:
    if not attributes_match_template(data.attributes, data.attribute_template_id):
        raise BadRequestException('Attributes do not match attribute template')
    encoded_item_name = encode_label_for_ltree(data.name)
    item_model_data = {
        'parent': data.parent,
        'parent_path': Ltree(f'{encode_path_for_ltree(data.parent_path)}') if data.parent_path else None,
        'archived': False,
        'type': data.type,
        'zone': data.zone,
        'name': encoded_item_name,
        'size': data.size,
        'owner': data.owner,
        'container_code': data.container_code,
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
        'extra': {
            'tags': data.tags,
            'system_tags': data.system_tags,
            'attributes': {str(data.attribute_template_id): data.attributes} if data.attributes else {},
        },
    }
    extended = ExtendedModel(**extended_model_data)
    db.session.add_all([item, storage, extended])
    db.session.commit()
    db.session.refresh(item)
    db.session.refresh(storage)
    db.session.refresh(extended)
    return combine_item_tables((item, storage, extended))


def create_items(data: POSTItems, api_response: APIResponse):
    results = []
    for item in data.items:
        results.append(create_item(item))
    api_response.result = results
    api_response.total = len(results)


def update_item(item_id: UUID, data: PUTItem) -> dict:
    if not attributes_match_template(data.attributes, data.attribute_template_id):
        raise BadRequestException('Attributes do not match attribute template')
    item = db.session.query(ItemModel).filter_by(id=item_id).first()
    encoded_item_name = encode_label_for_ltree(data.name)
    item.parent = data.parent
    item.parent_path = Ltree(f'{encode_path_for_ltree(data.parent_path)}') if data.parent_path else None
    item.type = data.type
    item.zone = data.zone
    item.name = encoded_item_name
    item.size = data.size
    item.owner = data.owner
    item.container_code = data.container_code
    item.container_type = data.container_type
    item.last_updated_time = datetime.utcnow()
    storage = db.session.query(StorageModel).filter_by(item_id=item_id).first()
    storage.location_uri = data.location_uri
    storage.version = data.version
    extended = db.session.query(ExtendedModel).filter_by(item_id=item_id).first()
    extended.extra = {
        'tags': data.tags,
        'system_tags': data.system_tags,
        'attributes': {str(data.attribute_template_id): data.attributes} if data.attributes else {},
    }
    db.session.commit()
    db.session.refresh(item)
    db.session.refresh(storage)
    db.session.refresh(extended)
    return combine_item_tables((item, storage, extended))


def update_items(ids: list[UUID], data: PUTItems, api_response: APIResponse):
    results = []
    for i in range(0, len(ids)):
        results.append(update_item(ids[i], data.items[i]))
    api_response.result = results
    api_response.total = len(results)


def archive_item_by_id(params: PATCHItem, api_response: APIResponse):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id == params.id)
    )
    item_result = item_query.first()
    item = item_result[0]
    item.archived = params.archived
    item.last_updated_time = datetime.utcnow()
    if params.archived:
        item.name = get_available_file_name(item.container_code, item.zone, item.name, None, True)
        item.restore_path = item.parent_path
        item.parent_path = None
    else:
        item.name = get_available_file_name(item.container_code, item.zone, item.name, item.restore_path, False)
        item.parent_path = item.restore_path
        item.restore_path = None
    db.session.commit()
    db.session.refresh(item)
    api_response.result = combine_item_tables(item_result)


def delete_item_by_id(id: UUID, api_response: APIResponse):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id == id)
    )
    for row in item_query.first():
        db.session.delete(row)
    db.session.commit()
    api_response.total = 0
    api_response.num_of_pages = 0


def delete_items_by_ids(ids: list[UUID], api_response: APIResponse):
    for id in ids:
        delete_item_by_id(id, api_response)
