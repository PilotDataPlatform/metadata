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

import uuid
from fastapi_sqlalchemy import db
from app.graphql.models import Item
from app.models.sql_items import ItemModel

def get_item_by_id(id: uuid.UUID):
    db_item = (
        db.session.query(ItemModel).filter(ItemModel.id == id)
    ).first()
    if db_item is not None:
        item_dict = db_item.to_dict()
        return Item(
            id=item_dict['id'],
            name=item_dict['name'],
            owner=item_dict['owner'],
            type=item_dict['type'],
            parent_path=item_dict['parent_path']
            )
    else:
        raise Exception("Not Found");
