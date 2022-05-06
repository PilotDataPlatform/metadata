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

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from app.config import ConfigClass

Base = declarative_base()


class CollectionsModel(Base):
    __tablename__ = 'collections'
    __table_args__ = {'schema': ConfigClass.METADATA_SCHEMA}
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String())
    container_code = Column(String())
    owner = Column(String())

    def __init__(self, id, name, container_code, owner):
        self.id = id
        self.name = name
        self.container_code = container_code
        self.owner = owner

    def to_dict(self):
        result = {}
        for field in ['id', 'name', 'container_code', 'owner']:
            result[field] = str(getattr(self, field))
        return result

