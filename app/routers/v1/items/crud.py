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

import time
import uuid
from datetime import datetime
from uuid import UUID

from fastapi_sqlalchemy import db
from sqlalchemy.sql import expression
from sqlalchemy_utils import Ltree
from sqlalchemy_utils.types.ltree import LQUERY

from app.app_utils import decode_label_from_ltree
from app.app_utils import decode_path_from_ltree
from app.app_utils import encode_label_for_ltree
from app.app_utils import encode_path_for_ltree
from app.models.base_models import APIResponse
from app.models.models_items import GETItem
from app.models.models_items import GETItemsByIDs
from app.models.models_items import GETItemsByLocation
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
from app.routers.router_exceptions import EntityNotFoundException
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
    if not item:
        return encoded_item_name
    decoded_item_name = decode_label_from_ltree(encoded_item_name)
    decoded_item_extension = ''
    if '.' in decoded_item_name:
        item_name_split = decoded_item_name.split('.', 1)
        decoded_item_name = item_name_split[0]
        decoded_item_extension = '.' + item_name_split[1]
    timestamp = round(time.time())
    decoded_item_name_new = f'{decoded_item_name}_{timestamp}{decoded_item_extension}'
    encoded_item_name_new = encode_label_for_ltree(decoded_item_name_new)
    return encoded_item_name_new


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


def get_items_by_ids(params: GETItemsByIDs, ids: list[UUID], api_response: APIResponse):
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id.in_(ids))
    )
    paginate(params, api_response, item_query, combine_item_tables)


def get_items_by_location(params: GETItemsByLocation, api_response: APIResponse):
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
        search_path = encode_path_for_ltree(params.parent_path)
        if params.recursive:
            search_path += '.*'
        item_query = item_query.filter(
            ItemModel.restore_path.lquery(expression.cast(search_path, LQUERY))
            if params.archived
            else ItemModel.parent_path.lquery(expression.cast(search_path, LQUERY)),
        )
    else:
        if not params.recursive:
            item_query = item_query.filter(ItemModel.parent_path == None)
    paginate(params, api_response, item_query, combine_item_tables)


def create_item(data: POSTItem) -> dict:
    if not attributes_match_template(data.attributes, data.attribute_template_id):
        raise BadRequestException('Attributes do not match attribute template')
    encoded_item_name = encode_label_for_ltree(data.name)
    item_model_data = {
        'id': data.id if data.id else uuid.uuid4(),
        'parent': data.parent if data.parent else None,
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
    item = db.session.query(ItemModel).filter_by(id=item_id).first()
    if data.parent != '':
        item.parent = data.parent if data.parent else None
    if data.parent_path != '':
        item.parent_path = Ltree(f'{encode_path_for_ltree(data.parent_path)}') if data.parent_path else None
    if data.type:
        item.type = data.type
    if data.zone:
        item.zone = data.zone
    if data.name:
        item.name = encode_label_for_ltree(data.name)
    if data.size:
        item.size = data.size
    if data.owner:
        item.owner = data.owner
    if data.container_code:
        item.container_code = data.container_code
    if data.container_type:
        item.container_type = data.container_type
    item.last_updated_time = datetime.utcnow()
    storage = db.session.query(StorageModel).filter_by(item_id=item_id).first()
    if data.location_uri:
        storage.location_uri = data.location_uri
    if data.version:
        storage.version = data.version
    extended = db.session.query(ExtendedModel).filter_by(item_id=item_id).first()
    extra = {}
    if data.tags:
        extra['tags'] = data.tags
    if data.system_tags:
        extra['system_tags'] = data.system_tags
    if data.attribute_template_id and data.attributes:
        if not attributes_match_template(data.attributes, data.attribute_template_id):
            raise BadRequestException('Attributes do not match attribute template')
        extra['attributes'] = ({str(data.attribute_template_id): data.attributes} if data.attributes else {},)
    if extra:
        extended.extra = extra
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


def get_restore_destination_id(container_code: str, zone: int, restore_path: Ltree) -> UUID:
    decoded_restore_path = decode_path_from_ltree(str(restore_path))
    destination_name = decoded_restore_path
    destination_path = None
    decoded_restore_path_labels = decoded_restore_path.split('.')
    if len(decoded_restore_path_labels) > 1:
        destination_name = decoded_restore_path_labels[-1]
        destination_path = '.'.join(decoded_restore_path_labels[:-1])
    destination_query = db.session.query(ItemModel).filter(
        ItemModel.container_code == container_code,
        ItemModel.zone == zone,
        ItemModel.archived == False,
        ItemModel.name == encode_label_for_ltree(destination_name),
    )
    if destination_path:
        destination_query = destination_query.filter(
            ItemModel.parent_path.lquery(expression.cast(encode_path_for_ltree(destination_path), LQUERY))
        )
    destination = destination_query.first()
    if destination:
        return destination.id


def archive_item(item: ItemModel, trash_item: bool, parent: bool):
    if item.archived != trash_item:
        if trash_item:
            if parent:
                item.name = get_available_file_name(item.container_code, item.zone, item.name, None, True)
                item.parent = None
            item.restore_path = item.parent_path
            item.parent_path = None
        else:
            if parent:
                restore_destination_id = get_restore_destination_id(item.container_code, item.zone, item.restore_path)
                if not restore_destination_id:
                    raise BadRequestException('Restore destination does not exist')
                item.parent = restore_destination_id
                item.name = get_available_file_name(item.container_code, item.zone, item.name, item.restore_path, False)
            item.parent_path = item.restore_path
            item.restore_path = None
        item.archived = trash_item
        item.last_updated_time = datetime.utcnow()


def archive_item_by_id(params: PATCHItem, api_response: APIResponse):
    root_item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id == params.id)
    )
    root_item_result = root_item_query.first()
    if not root_item_result:
        raise EntityNotFoundException()
    if root_item_result[0].type == 'name_folder':
        raise BadRequestException('Name folders cannot be archived or restored')
    children_result = []
    if root_item_result[0].type == 'folder':
        search_path = (
            f'{root_item_result[0].restore_path}.{root_item_result[0].name}.*'
            if root_item_result[0].archived
            else f'{root_item_result[0].parent_path}.{root_item_result[0].name}.*'
        )
        children_item_query = (
            db.session.query(ItemModel, StorageModel, ExtendedModel)
            .join(StorageModel, ExtendedModel)
            .filter(
                ItemModel.container_code == root_item_result[0].container_code,
                ItemModel.zone == root_item_result[0].zone,
                ItemModel.archived == root_item_result[0].archived,
                ItemModel.restore_path.lquery(expression.cast(search_path, LQUERY))
                if root_item_result[0].archived
                else ItemModel.parent_path.lquery(expression.cast(search_path, LQUERY)),
            )
        )
        children_result = children_item_query.all()
    all_items = []
    try:
        archive_item(root_item_result[0], params.archived, True)
        all_items.append(root_item_result)
        for child in children_result:
            archive_item(child[0], params.archived, False)
            all_items.append(child)
    except BadRequestException:
        raise
    db.session.commit()
    results = []
    for item in all_items:
        db.session.refresh(item[0])
        results.append(combine_item_tables(item))
    api_response.result = results
    api_response.total = len(results)


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
