from common import LoggerFactory
from fastapi_sqlalchemy import db

from app.models.sql_attribute_templates import AttributeTemplateModel
from app.models.sql_extended import ExtendedModel
from app.models.sql_items import ItemModel
from app.models.sql_items_collections import ItemsCollectionsModel
from app.models.sql_storage import StorageModel

_logger = LoggerFactory('api_health').get_logger()

def opsdb_check():
    try:
        db.session.query(ItemModel).first()
    except Exception as e:
        _logger.error(f'Could not connect to metadata.items table: {e}')
        return False

    try:
        db.session.query(ExtendedModel).first()
    except Exception as e:
        _logger.error(f'Could not connect to metadata.extended table: {e}')
        return False

    try:
        db.session.query(StorageModel).first()
    except Exception as e:
        _logger.error(f'Could not connect to metadata.storage table: {e}')
        return False

    try:
        db.session.query(AttributeTemplateModel).first()
    except Exception as e:
        _logger.error(f'Could not connect to metadata.attribute_templates table: {e}')
        return False

    try:
        db.session.query(ItemsCollectionsModel).first()
    except Exception as e:
        _logger.error(f'Could not connect to metadata.items_collections table: {e}')
        return False

    return True
