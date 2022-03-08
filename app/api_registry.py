from fastapi import FastAPI
from fastapi_health import health
from fastapi_sqlalchemy import db

from .routers.v1 import api_hello_world


def is_db_online():
    return db.session is not None


def api_registry(app: FastAPI):
    app.include_router(api_hello_world.router, prefix='/v1/hello-world', tags=['test'])
    app.add_api_route('/v1/health', health([is_db_online]), tags=['health'])
