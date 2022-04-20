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
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware

from .api_registry import api_registry
from .config import ConfigClass

app = FastAPI(
    title='Metadata service',
    description='Create and update file metadata',
    docs_url='/v1/api-doc',
    version=ConfigClass.version,
)
app.add_middleware(DBSessionMiddleware, db_url=ConfigClass.SQLALCHEMY_DATABASE_URI)

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

api_registry(app)
