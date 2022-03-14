from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import LtreeType

from app.config import ConfigClass
import uuid

Base = declarative_base()


class ItemsModel(Base):
    __tablename__ = 'items'
    id = Column(UUID, unique=True, primary_key=True, default=uuid.uuid4)
    parent = Column(UUID, nullable=False)
    path = Column(LtreeType(), nullable=False)
    type = Column(Enum('file', 'folder', name='type_enum', create_type=False), nullable=False)
    zone = Column(Integer(), nullable=False)
    name = Column(String(), nullable=False)
    size = Column(Integer())
    owner = Column(String())
    container = Column(UUID())
    container_type = Column(Enum('project', 'dataset', name='container_enum', create_type=False), nullable=False)


    __table_args__ = ({'schema': ConfigClass.METADATA_SCHEMA},)

    def __init__(self, parent, path, type, zone, name, size, owner, container, container_type):
        self.parent = parent
        self.path = path
        self.type = type
        self.zone = zone
        self.name = name
        self.size = size
        self.owner = owner
        self.container = container
        self.container_type = container_type

    def to_dict(self):
        return {
            'id': self.id,
            'parent': self.parent,
            'path': self.path,
            'type': self.type,
            'zone': self.zone,
            'name': self.name,
            'size': self.size,
            'owner': self.owner,
            'container': self.container,
            'container_type': self.container_type
        }
