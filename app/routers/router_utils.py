from pydantic import BaseModel

from app.models.base_models import APIResponse
from app.models.sql_items import Base


def paginate(params: BaseModel, api_response: APIResponse, items: Base):
    total = items.count()
    items = items.limit(params.page_size).offset(params.page * params.page_size)
    items = items.all()
    results = []
    for item in items:
        results.append(item.to_dict())
    api_response.page = params.page
    api_response.num_of_pages = int(int(total) / int(params.page_size))
    api_response.total = total
    api_response.result = results
