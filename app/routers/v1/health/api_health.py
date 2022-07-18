from common import LoggerFactory
from fastapi_sqlalchemy import db

_logger = LoggerFactory('api_health').get_logger()

def opsdb_check():
    try:
        return db.session is not None
    except Exception as e:
        _logger.error(f'OpsDB health check failed: {e}')
        return False
