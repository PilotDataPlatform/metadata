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

from fastapi import FastAPI
from fastapi_health import health
from fastapi_sqlalchemy import db

from .routers.v1.attribute_templates import api_attribute_templates
from .routers.v1.collections import api_collections
from .routers.v1.items import api_items
from .graphql.schema import graphql_app


def is_db_online():
    return db.session is not None


def api_registry(app: FastAPI):
    app.add_api_route('/v1/health/', health([is_db_online]), tags=['Health'])
    app.include_router(api_items.router, prefix='/v1/item', tags=['Items'])
    app.include_router(api_items.router_bulk, prefix='/v1/items', tags=['Items'])
    app.include_router(api_attribute_templates.router, prefix='/v1/template', tags=['Attribute templates'])
    app.include_router(api_collections.router, prefix='/v1/collection', tags=['Collections'])
    app.include_router(graphql_app, prefix='/graphql')
