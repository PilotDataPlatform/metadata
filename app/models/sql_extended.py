import uuid

from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

from app.config import ConfigClass

Base = declarative_base()


class ExtendedModel(Base):
    __tablename__ = 'extended'
    id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    extra = Column(JSON())

    __table_args__ = ({'schema': ConfigClass.METADATA_SCHEMA},)

    def __init__(self, extra):
        self.parent = extra

    def to_dict(self):
        return {'id': self.id, 'extra': self.extra}
