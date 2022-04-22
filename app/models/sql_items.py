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

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import LtreeType

from app.app_utils import decode_label_from_ltree
from app.app_utils import decode_path_from_ltree
from app.config import ConfigClass

Base = declarative_base()


class ItemModel(Base):
    __tablename__ = 'items'
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True)
    parent = Column(UUID(as_uuid=True))
    parent_path = Column(LtreeType())
    restore_path = Column(LtreeType())
    archived = Column(Boolean(), nullable=False)
    type = Column(Enum('file', 'folder', 'name_folder', name='type_enum', create_type=False), nullable=False)
    zone = Column(Integer(), nullable=False)
    name = Column(String(), nullable=False)
    size = Column(Integer())
    owner = Column(String())
    container_code = Column(String(), nullable=False)
    container_type = Column(Enum('project', 'dataset', name='container_enum', create_type=False), nullable=False)
    created_time = Column(DateTime(), default=datetime.utcnow, nullable=False)
    last_updated_time = Column(DateTime(), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index(
            'name_folder_unique',
            'zone',
            'name',
            'container_code',
            'container_type',
            unique=True,
            postgresql_where=Column('type') == 'name_folder',
        ),
        {'schema': ConfigClass.METADATA_SCHEMA},
    )

    def __init__(self, parent, parent_path, archived, type, zone, name, size, owner, container_code, container_type):
        self.id = uuid.uuid4()
        self.parent = parent
        self.parent_path = parent_path
        self.archived = archived
        self.type = type
        self.zone = zone
        self.name = name
        self.size = size
        self.owner = owner
        self.container_code = container_code
        self.container_type = container_type

    def to_dict(self):
        return {
            'id': str(self.id),
            'parent': str(self.parent) if self.parent else None,
            'parent_path': decode_path_from_ltree(str(self.parent_path)) if self.parent_path else None,
            'restore_path': decode_path_from_ltree(str(self.restore_path)) if self.restore_path else None,
            'archived': self.archived,
            'type': self.type,
            'zone': self.zone,
            'name': decode_label_from_ltree(self.name),
            'size': self.size,
            'owner': self.owner,
            'container_code': self.container_code,
            'container_type': self.container_type,
            'created_time': str(self.created_time),
            'last_updated_time': str(self.last_updated_time),
        }
