# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Callable

from common import LoggerFactory
from pydantic import BaseModel

from app.models.base_models import APIResponse
from app.models.base_models import EAPIResponseCode
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
    api_response.num_of_pages = int(int(total) / int(params.page_size)) + 1
    api_response.total = total
    api_response.result = results


def set_api_response_error(api_response: APIResponse, message: str, code: EAPIResponseCode, _logger: LoggerFactory):
    _logger.exception(message)
    api_response.set_error_msg(message)
    api_response.set_code(code)
    api_response.total = 0
    api_response.num_of_pages = 0
