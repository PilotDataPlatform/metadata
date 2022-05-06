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

import json
from uuid import UUID

from fastapi_sqlalchemy import db

from app.config import ConfigClass
from app.models.base_models import APIResponse
from app.models.base_models import EAPIResponseCode
from app.models.models_collections import DELETECollectionItems
from app.models.models_collections import GETCollection
from app.models.models_collections import GETCollectionItems
from app.models.models_collections import POSTCollection
from app.models.models_collections import POSTCollectionItems
from app.models.models_collections import PUTCollections
from app.models.sql_collections import CollectionsModel
from app.models.sql_extended import ExtendedModel
from app.models.sql_items import ItemModel
from app.models.sql_items_collections import ItemsCollectionsModel
from app.models.sql_storage import StorageModel
from app.routers.router_exceptions import BadRequestException
from app.routers.router_utils import paginate
from app.routers.v1.items.utils import combine_item_tables


def get_user_collections(params: GETCollection, api_response: APIResponse):
    collection_query = (
        db.session.query(CollectionsModel).filter(CollectionsModel.owner == params.owner,
                                                  CollectionsModel.container_code == params.container_code)
    )
    collection_result = collection_query.all()

    if collection_result:
        result = [collection.to_dict() for collection in collection_result]
        api_response.result = result
        api_response.total = len(result)
    else:
        api_response.code = EAPIResponseCode.not_found
        api_response.total = 0


def get_items_per_collection(params: GETCollectionItems, api_response: APIResponse):
    collection_query = (
        db.session.query(ItemModel.id).join(ItemsCollectionsModel,
                                            ItemModel.id == ItemsCollectionsModel.item_id).filter_by(
            collection_id=params.id)
    )
    collection_result = collection_query.all()
    requested_uuids = [uuid[0] for uuid in collection_result]

    if collection_result:
        item_query = (
            db.session.query(ItemModel, StorageModel, ExtendedModel).join(StorageModel, ExtendedModel)
            .filter(ItemModel.id.in_(requested_uuids))
        )
        paginate(params, api_response, item_query, combine_item_tables)
    else:
        api_response.total = 0


def create_collection(data: POSTCollection, api_response: APIResponse):
    collection_query = (
        db.session.query(CollectionsModel).filter(CollectionsModel.owner == data.owner,
                                                  CollectionsModel.container_code == data.container_code)
    )
    collection_result = collection_query.all()

    if len(collection_result) == ConfigClass.MAX_COLLECTIONS:
        raise BadRequestException(f'Cannot create more than {ConfigClass.MAX_COLLECTIONS} collections')
    elif data.name in [collection.name for collection in collection_result]:
        raise BadRequestException(f'Collection {data.name} already exists')
    else:
        model_data = {'id': data.id, 'owner': data.owner, 'container_code': data.container_code,
                      'name': data.name}
        collection = CollectionsModel(**model_data)
        db.session.add(collection)
        db.session.commit()
        db.session.refresh(collection)
        api_response.result = collection.to_dict()
        api_response.total = 1


def update_collection(data: PUTCollections, api_response: APIResponse):
    for collection in data.collections:
        query = (
            db.session.query(CollectionsModel).filter(CollectionsModel.id == collection.id,
                CollectionsModel.owner == data.owner,
                CollectionsModel.container_code == data.container_code)
        )
        query_result = query.one()
        if query_result:
            query_result.name = collection.name
            db.session.commit()
        else:
            raise BadRequestException(
                f'Collection with id {collection.id} and name {collection.name} does not exist')

    result = json.loads(data.json())
    api_response.result = result
    api_response.total = len(data.collections)


def add_items(data: POSTCollectionItems, api_response: APIResponse):
    # foreign key constraint ensures collection_id and item_id must exist in collection and items tables
    for item_id in data.item_ids:
        db.session.merge(ItemsCollectionsModel(collection_id=data.id, item_id=item_id))
    db.session.commit()
    result = json.loads(data.json())
    api_response.result = result
    api_response.total = len(data.item_ids)


def remove_items(data: DELETECollectionItems):
    # foreign key constraint ensures collection_id and item_id must exist in collection and items tables
    db.session.query(ItemsCollectionsModel).filter(ItemsCollectionsModel.collection_id == data.id,
                                                   ItemsCollectionsModel.item_id.in_(data.item_ids)).delete()

    db.session.commit()


def remove_collection(collection_id: UUID):
    db.session.query(CollectionsModel).filter(CollectionsModel.id == collection_id).delete()
    db.session.commit()
