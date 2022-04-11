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

import base64
import math
import re


def encode_label_for_ltree(raw_string: str) -> str:
    base32_string = str(base64.b32encode(raw_string.encode('utf-8')), 'utf-8')
    return re.sub('=', '', base32_string)


def encode_path_for_ltree(raw_path: str) -> str:
    labels = raw_path.split('.')
    path = ''
    for label in labels:
        path += f'{encode_label_for_ltree(label)}.'
    return path[:-1]


def decode_label_from_ltree(encoded_string: str) -> str:
    missing_padding = math.ceil(len(encoded_string) / 8) * 8 - len(encoded_string)
    if missing_padding:
        encoded_string += '=' * missing_padding
    utf8_string = base64.b32decode(encoded_string.encode('utf-8')).decode('utf-8')
    return utf8_string


def decode_path_from_ltree(encoded_path: str) -> str:
    labels = encoded_path.split('.')
    path = ''
    for label in labels:
        path += f'{decode_label_from_ltree(label)}.'
    return path[:-1]
