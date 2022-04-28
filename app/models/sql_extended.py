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

from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from app.config import ConfigClass

from .sql_items import ItemModel

Base = declarative_base()


class ExtendedModel(Base):
    __tablename__ = 'extended'
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True)
    item_id = Column(UUID(as_uuid=True), ForeignKey(ItemModel.id), unique=True)
    extra = Column(JSON())

    __table_args__ = ({'schema': ConfigClass.METADATA_SCHEMA},)

    def __init__(self, item_id, extra):
        self.id = uuid.uuid4(),
        self.item_id = item_id,
        self.extra = extra

    def to_dict(self):
        return {'id': str(self.id), 'item_id': str(self.item_id), 'extra': self.extra}
