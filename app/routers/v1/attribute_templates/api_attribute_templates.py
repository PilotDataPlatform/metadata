from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from fastapi.responses import JSONResponse

router = APIRouter()


@cbv(router)
class APIAttributeTemplates:
    @router.get('/', summary='Get an attribute template')
    async def get_attribute_template(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.post('/', summary='Create a new attribute template')
    async def create_attribute_template(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.put('/', summary='Update an attribute template')
    async def update_attribute_template(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)

    @router.delete('/', summary='Delete an attribute template')
    async def delete_attribute_template(self):
        return JSONResponse(content={'message': 'Placeholder'}, status_code=501)
