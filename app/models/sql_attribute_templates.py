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
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from app.config import ConfigClass

Base = declarative_base()


class AttributeTemplateModel(Base):
    __tablename__ = 'attribute_templates'
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True)
    name = Column(String(), nullable=False)
    project_code = Column(String(), nullable=False)
    attributes = Column(JSON())

    __table_args__ = ({'schema': ConfigClass.METADATA_SCHEMA},)

    def __init__(self, name, project_code, attributes):
        self.id = uuid.uuid4()
        self.name = name
        self.project_code = project_code
        self.attributes = attributes

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'project_code': self.project_code,
            'attributes': self.attributes,
        }
