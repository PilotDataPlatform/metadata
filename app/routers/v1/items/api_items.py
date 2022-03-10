from fastapi import APIRouter
from fastapi_utils.cbv import cbv

router = APIRouter()


@cbv(router)
class APIItems:
    @router.get('/', summary='Get one or more items or check if an item exists')
    async def get_items(self):
        return {'message': 'Placeholder'}

    @router.post('/', summary='Create a new item')
    async def create_item(self):
        return {'message': 'Placeholder'}

    @router.put('/', summary='Update an item')
    async def update_item(self):
        return {'message': 'Placeholder'}

    @router.patch('/', summary='Move an item to the trash')
    async def trash_item(self):
        return {'message': 'Placeholder'}

    @router.delete('/', summary='Permanently delete an item')
    async def delete_item(self):
        return {'message': 'Placeholder'}
