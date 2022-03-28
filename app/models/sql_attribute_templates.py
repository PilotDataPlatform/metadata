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
    project_id = Column(UUID(as_uuid=True), nullable=False)
    attributes = Column(JSON())

    __table_args__ = ({'schema': ConfigClass.METADATA_SCHEMA},)

    def __init__(self, name, project_id, attributes):
        self.id = uuid.uuid4()
        self.name = name
        self.project_id = project_id
        self.attributes = attributes

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'project_id': str(self.project_id),
            'attributes': self.attributes,
        }
