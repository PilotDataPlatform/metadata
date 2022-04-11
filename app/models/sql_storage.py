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

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from app.config import ConfigClass

from .sql_items import ItemModel

Base = declarative_base()


class StorageModel(Base):
    __tablename__ = 'storage'
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True)
    item_id = Column(UUID(as_uuid=True), ForeignKey(ItemModel.id), unique=True)
    location_uri = Column(String())
    version = Column(String())

    __table_args__ = ({'schema': ConfigClass.METADATA_SCHEMA},)

    def __init__(self, item_id, location_uri, version):
        self.id = (uuid.uuid4(),)
        self.item_id = (item_id,)
        self.location_uri = (location_uri,)
        self.version = version

    def to_dict(self):
        return {
            'id': str(self.id),
            'item_id': str(self.item_id),
            'location_uri': self.location_uri,
            'version': self.version,
        }
