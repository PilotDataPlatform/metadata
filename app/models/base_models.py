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

from enum import Enum

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class EAPIResponseCode(Enum):
    success = 200
    bad_request = 400
    unauthorized = 401
    forbidden = 403
    not_found = 404
    conflict = 409
    too_large = 413
    internal_error = 500


class APIResponse(BaseModel):
    code: EAPIResponseCode = EAPIResponseCode.success
    error_msg: str = ''
    page: int = 0
    total: int = 1
    num_of_pages: int = 1
    result = []

    def json_response(self) -> JSONResponse:
        data = self.dict()
        data['code'] = self.code.value
        return JSONResponse(status_code=self.code.value, content=data)

    def set_error_msg(self, error_msg):
        self.error_msg = error_msg

    def set_code(self, code):
        self.code = code


class PaginationRequest(BaseModel):
    page: int = 0
    page_size: int = 25
    order: str = 'asc'
    sorting: str = 'createTime'
