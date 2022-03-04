from fastapi import APIRouter
from fastapi_utils.cbv import cbv

router = APIRouter()

# This file is for early testing only
# Delete when a functional endpoint is added

@cbv(router)
class APIHelloWorld:
    @router.get(
        '/', summary='Test that API is functioning'
    )
    async def hello_world(self):
        return { 'message': 'Hello world' }
