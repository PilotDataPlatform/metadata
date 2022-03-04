from fastapi import APIRouter
from fastapi_utils.cbv import cbv

router = APIRouter()

@cbv(router)
class APIHelloWorld:
    @router.get(
        '/', summary='Test that API is functioning'
    )
    async def hello_world(self):
        return { 'message': 'Hello world' }
