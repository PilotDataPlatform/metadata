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

from fastapi_sqlalchemy import db
import strawberry
from strawberry.fastapi import GraphQLRouter
from app.graphql.models import Item
from app.graphql.resolvers import get_item_by_id
from app.app_utils import encode_path_for_ltree
from sqlalchemy_utils import Ltree
import uuid
from typing import Optional

from app.models.sql_items import ItemModel

@strawberry.type
class Query:
    item: 'Item' = strawberry.field(resolver=get_item_by_id)

@strawberry.type
class Mutation:
    @strawberry.field
    def add_item(self, name: str, owner: str, zone: int, type: str, size: int, container_code: str, container_type: str, parent: Optional[str] = None, parent_path: Optional[str] = None) -> Item:
        item_model_data = {
            'id': uuid.uuid4(),
            'parent': parent if parent is not None else None,
            'parent_path': Ltree(f'{encode_path_for_ltree(parent_path)}') if parent_path is not None else None,
            'archived': False,
            'type': type,
            'zone': zone,
            'name': name,
            'size': size,
            'owner': owner,
            'container_code': container_code,
            'container_type': container_type,
        }
        item = ItemModel(**item_model_data)
        db.session.add_all([item])
        db.session.commit()
        db.session.refresh(item)
        
        return Item(item.id, item.name, item.owner, item.type, item.parent_path)


schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(schema)
