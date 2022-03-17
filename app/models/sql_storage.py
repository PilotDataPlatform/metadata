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
