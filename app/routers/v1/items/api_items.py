from fastapi import APIRouter
from fastapi_utils.cbv import cbv

router = APIRouter()


@cbv(router)
class APIItems:
    @router.get('/', summary='Get item(s)')
    async def get_items(self):
        return {'message': 'Hello world'}
