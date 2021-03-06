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

from uuid import UUID

from fastapi_sqlalchemy import db

from app.models.sql_collections import CollectionsModel
from app.routers.router_exceptions import EntityNotFoundException


def validate_collection(collection_id: UUID):
    collection_query = (
            db.session.query(CollectionsModel).filter(CollectionsModel.id == collection_id))
    collection_result = collection_query.first()
    if not collection_result:
        raise EntityNotFoundException(f'Collection {collection_id} does not exist')
