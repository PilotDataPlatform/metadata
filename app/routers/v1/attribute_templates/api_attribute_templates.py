from fastapi import APIRouter
from fastapi_utils.cbv import cbv

router = APIRouter()


@cbv(router)
class APIAttributeTemplates:
    @router.get('/', summary='Get an attribute template')
    async def get_attribute_template(self):
        return {'message': 'Hello world'}

    @router.post('/', summary='Create a new attribute template')
    async def create_attribute_template(self):
        return {'message': 'Hello world'}

    @router.put('/', summary='Update an attribute template')
    async def update_attribute_template(self):
        return {'message': 'Hello world'}

    @router.delete('/', summary='Delete an attribute template')
    async def delete_attribute_template(self):
        return {'message': 'Hello world'}
