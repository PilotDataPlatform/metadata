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

from app.routers.v1.health.api_health import opsdb_check

from .routers.v1.attribute_templates import api_attribute_templates
from .routers.v1.collections import api_collections
from .routers.v1.items import api_items


def api_registry(app: FastAPI):
    app.add_api_route('/v1/health/', health([opsdb_check]), success_status=204, tags=['Health'])
    app.include_router(api_items.router, prefix='/v1/item', tags=['Items'])
    app.include_router(api_items.router_bulk, prefix='/v1/items', tags=['Items'])
    app.include_router(api_attribute_templates.router, prefix='/v1/template', tags=['Attribute templates'])
    app.include_router(api_collections.router, prefix='/v1/collection', tags=['Collections'])
