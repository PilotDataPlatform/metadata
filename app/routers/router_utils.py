from typing import Callable

from pydantic import BaseModel

from app.models.base_models import APIResponse
from app.models.sql_items import Base


def paginate(params: BaseModel, api_response: APIResponse, query: Base, expand_func: Callable) -> APIResponse:
    total = query.count()
    query = query.limit(params.page_size).offset(params.page * params.page_size)
    items = query.all()
    results = []
    for item in items:
        if expand_func:
            item_dict = expand_func(item)
            results.append(item_dict)
        else:
            results.append(item.to_dict())
    api_response.page = params.page
    api_response.num_of_pages = int(int(total) / int(params.page_size))
    api_response.total = total
    api_response.result = results
