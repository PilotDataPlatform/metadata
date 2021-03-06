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
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from app.config import ConfigClass
from app.models.sql_collections import CollectionsModel
from app.models.sql_items import ItemModel

Base = declarative_base()


class ItemsCollectionsModel(Base):
    __tablename__ = 'items_collections'
    __table_args__ = {'schema': ConfigClass.METADATA_SCHEMA}
    item_id = Column(ForeignKey(ItemModel.id), primary_key=True)
    collection_id = Column(ForeignKey(CollectionsModel.id), primary_key=True)
