from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware

from .api_registry import api_registry
from .config import ConfigClass

app = FastAPI(
    title='Metadata service',
    description='Create and update file metadata',
    docs_url='/v1/api-doc',
    version=ConfigClass.version,
)
app.add_middleware(DBSessionMiddleware, db_url=ConfigClass.SQLALCHEMY_DATABASE_URI)

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

api_registry(app)
