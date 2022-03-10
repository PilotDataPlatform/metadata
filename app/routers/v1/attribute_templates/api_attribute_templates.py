from fastapi import APIRouter
from fastapi_utils.cbv import cbv

router = APIRouter()


@cbv(router)
class APIAttributeTemplates:
    @router.get('/', summary='Get attribute template')
    async def get_attribute_template(self):
        return {'message': 'Hello world'}
