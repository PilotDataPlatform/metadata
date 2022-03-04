from fastapi import FastAPI

from .routers.v1 import api_hello_world


def api_registry(app: FastAPI):
    app.include_router(api_hello_world.router, prefix='/v1/hello-world', tags=['test'])
