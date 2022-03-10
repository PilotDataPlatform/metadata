from fastapi import FastAPI
from fastapi_health import health
from fastapi_sqlalchemy import db

from .routers.v1.items import api_items
from .routers.v1.attribute_templates import api_attribute_templates


def is_db_online():
    return db.session is not None


def api_registry(app: FastAPI):
    app.add_api_route('/v1/health', health([is_db_online]), tags=['Health'])
    app.include_router(api_items.router, prefix='/v1/item', tags=['Items'])
    app.include_router(api_attribute_templates.router, prefix='/v1/template', tags=['Attribute templates'])
