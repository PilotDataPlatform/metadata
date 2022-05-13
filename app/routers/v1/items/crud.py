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
from app.models.models_items import PUTItemsBequeath
from app.models.sql_attribute_templates import AttributeTemplateModel
from app.models.sql_extended import ExtendedModel
from app.models.sql_items import ItemModel
from app.models.sql_storage import StorageModel
from app.routers.router_exceptions import BadRequestException
from app.routers.router_exceptions import EntityNotFoundException
from app.routers.router_utils import paginate
from app.routers.v1.items.utils import combine_item_tables
from app.routers.v1.items.utils import get_path_depth
from app.routers.v1.items.utils import get_relative_path_depth


def get_available_file_name(
    container_code: UUID,
    zone: int,
    item_name: str,
    encoded_item_path: Ltree,
    archived: bool,
) -> str:
    item = (
        db.session.query(ItemModel)
        .filter_by(
            container_code=container_code,
            zone=zone,
            name=item_name,
            parent_path=encoded_item_path,
            archived=archived,
        )
        .first()
    )
    if not item:
        return item_name
    item_extension = ''
    if '.' in item_name:
        item_name_split = item_name.split('.', 1)
        item_name = item_name_split[0]
        item_extension = '.' + item_name_split[1]
    timestamp = round(time.time())
    item_name_new = f'{item_name}_{timestamp}{item_extension}'
    return item_name_new


def get_item_children(root_item: ItemModel, group_by_depth: bool = False) -> dict:
    search_path = (
        f'{root_item.restore_path}.{encode_label_for_ltree(root_item.name)}.*'
        if root_item.archived
        else f'{root_item.parent_path}.{encode_label_for_ltree(root_item.name)}.*'
    )
    children_item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(
            ItemModel.container_code == root_item.container_code,
            ItemModel.zone == root_item.zone,
            ItemModel.archived == root_item.archived,
            ItemModel.restore_path.lquery(expression.cast(search_path, LQUERY))
            if root_item.archived
            else ItemModel.parent_path.lquery(expression.cast(search_path, LQUERY)),
        )
    )
    children = children_item_query.all()
    if not group_by_depth:
        return children
    layers = {}
    for item in children:
        depth = get_relative_path_depth(root_item, item[0])
        if depth not in layers:
            layers[depth] = []
        layers[depth].append(item)
    return layers


def move_item(item: ItemModel, new_parent_path: str, children: dict = None, depth: int = 1):
    if not children:
        children = get_item_children(item, True)
    item.parent_path = Ltree(encode_path_for_ltree(new_parent_path)) if new_parent_path else None
    if depth not in children:
        return
    layer = children[depth]
    for child in layer:
        move_item(child[0], f'{new_parent_path}.{item.name}' if new_parent_path else item.name, children, depth + 1)


def rename_item(
    root_item: ItemModel, item: ItemModel, old_name: str, new_name: str, children: dict = None, depth: int = 1
):
    if not children:
        children = get_item_children(item, True)
    if item == root_item:
        item.name = new_name
    else:
        decoded_parent_path = decode_path_from_ltree(item.parent_path)
        root_item_depth = get_path_depth(root_item)
        labels = decoded_parent_path.split('.')
        labels[root_item_depth] = new_name
        new_parent_path = '.'.join(labels)
        item.parent_path = Ltree(encode_path_for_ltree(new_parent_path))
    if depth not in children:
        return
    layer = children[depth]
    for child in layer:
        rename_item(root_item, child[0], old_name, new_name, children, depth + 1)


def attributes_match_template(attributes: dict, template_id: UUID) -> bool:
    if not template_id and not attributes:
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
    if params.type and params.type not in ['name_folder', 'folder', 'file']:
        raise BadRequestException(f'Invalid type {params.type}')
    if params.container_type and params.container_type not in ['project', 'dataset']:
        raise BadRequestException(f'Invalid container_type {params.container_type}')
    try:
        custom_sort = getattr(ItemModel, params.sorting).asc()
        if params.order == 'desc':
            custom_sort = getattr(ItemModel, params.sorting).desc()
    except:
        raise BadRequestException(f'Cannot sort by {params.sorting}')
    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(
            ItemModel.container_code == params.container_code,
            ItemModel.zone == params.zone,
            ItemModel.archived == params.archived,
        )
        .order_by(ItemModel.type, custom_sort)
    )
    if params.name:
        item_query = item_query.filter(ItemModel.name.like(params.name))
    if params.owner:
        item_query = item_query.filter(ItemModel.owner.like(params.owner))
    if params.type:
        item_query = item_query.filter(ItemModel.type == params.type)
    if params.container_type:
        item_query = item_query.filter(ItemModel.container_type == params.container_type)
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
    item_model_data = {
        'id': data.id if data.id else uuid.uuid4(),
        'parent': data.parent if data.parent else None,
        'parent_path': Ltree(f'{encode_path_for_ltree(data.parent_path)}') if data.parent_path else None,
        'archived': False,
        'type': data.type,
        'zone': data.zone,
        'name': data.name,
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
    if data.parent_path != '' and not item.archived:
        move_item(item, data.parent_path)
    if data.type:
        item.type = data.type
    if data.zone:
        item.zone = data.zone
    if data.name and not item.archived:
        rename_item(item, item, item.name, data.name)
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
        extra['attributes'] = {str(data.attribute_template_id): data.attributes} if data.attributes else {}
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
    decoded_restore_path = decode_path_from_ltree(restore_path)
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
        ItemModel.name == destination_name,
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
        children_result = get_item_children(root_item_result[0])
    all_items = []
    try:
        archive_item(root_item_result[0], params.archived, True)
        all_items.append(root_item_result)
        for child in children_result:
            archive_item(child[0], params.archived, False)
            all_items.append(child)
        if params.archived:
            move_item(root_item_result[0], None)
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
    root_item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id == id)
    )
    root_item_result = root_item_query.first()
    if root_item_result[0].type == 'folder':
        children_result = get_item_children(root_item_result[0])
        for child in children_result:
            for row in child:
                db.session.delete(row)
    for row in root_item_result:
        db.session.delete(row)
    db.session.commit()
    api_response.total = 0
    api_response.num_of_pages = 0


def delete_items_by_ids(ids: list[UUID], api_response: APIResponse):
    for id in ids:
        delete_item_by_id(id, api_response)


def bequeath_to_children(id: UUID, data: PUTItemsBequeath, api_response: APIResponse):
    if not attributes_match_template(data.attributes, data.attribute_template_id):
        raise BadRequestException('Attributes do not match attribute template')
    root_item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel)
        .join(StorageModel, ExtendedModel)
        .filter(ItemModel.id == id)
    )
    root_item_result = root_item_query.first()
    if not root_item_result:
        raise EntityNotFoundException()
    if root_item_result[0].type != 'folder':
        raise BadRequestException('Properties can only be bequeathed from folders')
    children_result = get_item_children(root_item_result[0])
    results = []
    for child in children_result:
        extra = {}
        if data.attribute_template_id and data.attributes:
            extra = {'attributes': {str(data.attribute_template_id): data.attributes} if data.attributes else {}}
        if data.system_tags:
            extra['system_tags'] = data.system_tags
        child[2].extra = extra
    db.session.commit()
    for child in children_result:
        db.session.refresh(child[2])
        results.append(combine_item_tables(child))
    api_response.result = results
    api_response.total = len(results)
