import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from app.config import ConfigClass

Base = declarative_base()


class StorageModel(Base):
    __tablename__ = 'storage'
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), unique=True)
    location_uri = Column(String())
    version = Column(String())

    __table_args__ = ({'schema': ConfigClass.METADATA_SCHEMA},)

    def __init__(self, item_id, location_uri, version):
        self.parent = item_id,
        self.location_uri = location_uri,
        self.version = version

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'location_uri': self.location_uri,
            'version': self.version,
        }
