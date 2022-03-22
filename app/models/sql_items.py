import uuid

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import LtreeType

from app.config import ConfigClass

Base = declarative_base()


class ItemModel(Base):
    __tablename__ = 'items'
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True)
    parent = Column(UUID(as_uuid=True), nullable=False)
    path = Column(LtreeType(), nullable=False)
    restore_path = Column(LtreeType())
    archived = Column(Boolean(), nullable=False)
    type = Column(Enum('file', 'folder', name='type_enum', create_type=False), nullable=False)
    zone = Column(Integer(), nullable=False)
    name = Column(String(), nullable=False)
    size = Column(Integer())
    owner = Column(String())
    container = Column(UUID(as_uuid=True))
    container_type = Column(Enum('project', 'dataset', name='container_enum', create_type=False), nullable=False)

    __table_args__ = ({'schema': ConfigClass.METADATA_SCHEMA},)

    def __init__(self, parent, path, archived, type, zone, name, size, owner, container, container_type):
        self.id = uuid.uuid4()
        self.parent = parent
        self.path = path
        self.archived = archived
        self.type = type
        self.zone = zone
        self.name = name
        self.size = size
        self.owner = owner
        self.container = container
        self.container_type = container_type

    def to_dict(self):
        return {
            'id': str(self.id),
            'parent': str(self.parent),
            'path': str(self.path),
            'restore_path': str(self.restore_path) if self.restore_path else None,
            'archived': self.archived,
            'type': self.type,
            'zone': self.zone,
            'name': self.name,
            'size': self.size,
            'owner': self.owner,
            'container': str(self.container),
            'container_type': self.container_type,
        }
