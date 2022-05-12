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
from datetime import datetime
from uuid import UUID

from fastapi_sqlalchemy import db

from app.config import ConfigClass
from app.models.base_models import APIResponse
from app.models.models_collections import DELETECollectionItems
from app.models.models_collections import GETCollection
from app.models.models_collections import GETCollectionID
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
    try:
        custom_sort = getattr(CollectionsModel, params.sorting).asc()
        if params.order == 'desc':
            custom_sort = getattr(CollectionsModel, params.sorting).desc()
    except Exception:
        raise BadRequestException(f'Cannot sort by {params.sorting}')

    collection_query = (
        db.session.query(CollectionsModel).filter(CollectionsModel.owner == params.owner,
                                                  CollectionsModel.container_code == params.container_code)
        .order_by(custom_sort)
    )

    paginate(params, api_response, collection_query, expand_func=False)


def get_collections_by_id(params: GETCollectionID, api_response: APIResponse):
    collection_query = (
        db.session.query(CollectionsModel).filter(CollectionsModel.id == params.id)
    )
    collection_result = collection_query.first()
    if collection_result:
        api_response.result = collection_result.to_dict()
        api_response.total = 1
    else:
        raise BadRequestException(f'Collection id {params.id} does not exist')


def get_items_per_collection(params: GETCollectionItems, api_response: APIResponse):
    try:
        custom_sort = getattr(ItemModel, params.sorting).asc()
        if params.order == 'desc':
            custom_sort = getattr(ItemModel, params.sorting).desc()
    except Exception:
        raise BadRequestException(f'Cannot sort by {params.sorting}')

    item_query = (
        db.session.query(ItemModel, StorageModel, ExtendedModel).join(StorageModel, ExtendedModel,
                                                                      ItemsCollectionsModel)
        .filter(ItemsCollectionsModel.collection_id == params.id, ItemModel.archived == params.archived)
        .order_by(ItemModel.container_type, custom_sort)
    )

    paginate(params, api_response, item_query, combine_item_tables)


def create_collection(data: POSTCollection, api_response: APIResponse):
    collection_query = (
        db.session.query(CollectionsModel).filter(CollectionsModel.owner == data.owner,
                                                  CollectionsModel.container_code == data.container_code)
    )
    collection_result = collection_query.all()
    if len(collection_result) == ConfigClass.MAX_COLLECTIONS:
        raise BadRequestException(f'Cannot create more than {ConfigClass.MAX_COLLECTIONS} collections')
    elif data.name in (collection.name for collection in collection_result):
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
    payload_ids = [str(collection.id) for collection in data.collections]
    payload_names = [collection.name for collection in data.collections]
    query = (
        db.session.query(CollectionsModel).filter(CollectionsModel.id.in_(payload_ids),
                                                  CollectionsModel.owner == data.owner,
                                                  CollectionsModel.container_code == data.container_code)
    )
    query_result = query.all()
    if len(query_result) is len(payload_ids):
        query_names = [i.name for i in query_result]
        collections_names_exist = list(set(payload_names).intersection(set(query_names)))

        if len(collections_names_exist) > 0:
            raise BadRequestException(f'Collection name(s) {collections_names_exist} already exists')

        else:
            for collection in data.collections:
                db.session.merge(CollectionsModel(id=collection.id, name=collection.name,
                                                  container_code=data.container_code, owner=data.owner,
                                                  last_updated_time=datetime.utcnow()))
            db.session.commit()
    else:
        if len(query_result) == 0:
            collections_not_exist = payload_ids
        else:
            query_ids = [str(i.id) for i in query_result]
            collections_not_exist = list(set(payload_ids) - set(query_ids))
        raise BadRequestException(f'Collection id(s) {collections_not_exist} do not exist')

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


def remove_collection(collection_id: UUID, api_response: APIResponse):
    db.session.query(CollectionsModel).filter(CollectionsModel.id == collection_id).delete()
    db.session.commit()
    api_response.total = 0
    api_response.num_of_pages = 0
