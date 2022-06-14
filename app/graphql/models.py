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

import typing
from typing import Optional
from fastapi_sqlalchemy import db
import strawberry
import uuid
from sqlalchemy_utils import Ltree

@strawberry.type
class Item:
    id: uuid.UUID
    name: str
    owner: str
    type: str
    container_code: str
    container_type: str
    parent_path: Optional[str]


@strawberry.type
class CreateItem:
    parent: uuid.UUID
    parent_path: str
    type: str
    zone: int
    name: str
    size: int
    owner: str
    container_code: str
    container_type: str
    location_uri: str
    version: str
    tags: list[str]
    system_tags: list[str]
    attribute_template_id: uuid.UUID
    attributes: dict
