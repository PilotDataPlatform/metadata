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
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from app.config import ConfigClass

Base = declarative_base()


class CollectionsModel(Base):
    __tablename__ = 'collections'
    __table_args__ = {'schema': ConfigClass.METADATA_SCHEMA}
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(), nullable=False)
    container_code = Column(String(), nullable=False)
    owner = Column(String(), nullable=False)
    created_time = Column(DateTime(), default=datetime.utcnow, nullable=False)
    last_updated_time = Column(DateTime(), default=datetime.utcnow, nullable=False)

    def __init__(self, name, container_code, owner, id=None, last_updated_time=None):
        self.id = id if id is not None else uuid.uuid4()
        self.name = name
        self.container_code = container_code
        self.owner = owner
        self.last_updated_time = last_updated_time if last_updated_time is not None else datetime.utcnow()

    def to_dict(self):
        return {'id': str(self.id), 'name': self.name, 'container_code': self.container_code, 'owner': self.owner,
                'created_time': str(self.created_time),
                'last_updated_time': str(self.last_updated_time),
                }
