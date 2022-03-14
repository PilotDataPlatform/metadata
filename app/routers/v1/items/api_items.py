from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv

router = APIRouter()


@cbv(router)
class APIItems:
    @router.get('/', summary='Get one or more items or check if an item exists')
    async def get_items(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.post('/', summary='Create a new item')
    async def create_item(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.put('/', summary='Update an item')
    async def update_item(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.patch('/', summary='Move an item to the trash')
    async def trash_item(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.delete('/', summary='Permanently delete an item')
    async def delete_item(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)
