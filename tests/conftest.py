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

import random
import uuid
from json import loads

import pytest
from fastapi.testclient import TestClient

from app.main import app

app = TestClient(app)


def generate_random_container_code() -> str:
    random_container_code = 'test_'
    for _ in range(8):
        random_container_code += chr(random.randint(32, 126))
    return random_container_code


@pytest.fixture(scope='function')
def test_items() -> dict:
    props = {
        'container_code': generate_random_container_code(),
        'ids': {
            'name_folder': str(uuid.uuid4()),
            'folder': str(uuid.uuid4()),
            'file_1': str(uuid.uuid4()),
            'file_2': str(uuid.uuid4()),
            'file_3': str(uuid.uuid4()),
        },
    }
    payload = {
        'items': [
            {
                'id': props['ids']['name_folder'],
                'parent': None,
                'parent_path': None,
                'type': 'name_folder',
                'zone': 0,
                'name': 'user',
                'size': 0,
                'owner': 'user',
                'container_code': props['container_code'],
                'container_type': 'project',
                'location_uri': '',
                'version': '',
            },
            {
                'id': props['ids']['folder'],
                'parent': props['ids']['name_folder'],
                'parent_path': 'user',
                'type': 'folder',
                'zone': 0,
                'name': 'test_folder',
                'size': 0,
                'owner': 'user',
                'container_code': props['container_code'],
                'container_type': 'project',
                'location_uri': '',
                'version': '',
                'tags': [],
                'system_tags': [],
            },
            {
                'id': props['ids']['file_1'],
                'parent': props['ids']['folder'],
                'parent_path': 'user.test_folder',
                'type': 'file',
                'zone': 0,
                'name': 'test_file_1.txt',
                'size': 100,
                'owner': 'user',
                'container_code': props['container_code'],
                'container_type': 'project',
                'location_uri': '',
                'version': '',
                'tags': [],
                'system_tags': [],
            },
            {
                'id': props['ids']['file_2'],
                'parent': props['ids']['folder'],
                'parent_path': 'user.test_folder',
                'type': 'file',
                'zone': 0,
                'name': 'test_file_2.txt',
                'size': 100,
                'owner': 'user',
                'container_code': props['container_code'],
                'container_type': 'project',
                'location_uri': '',
                'version': '',
                'tags': [],
                'system_tags': [],
            },
            {
                'id': props['ids']['file_3'],
                'parent': props['ids']['folder'],
                'parent_path': 'user.test_folder',
                'type': 'file',
                'zone': 0,
                'name': 'test_file_3.txt',
                'size': 100,
                'owner': 'user',
                'container_code': props['container_code'],
                'container_type': 'project',
                'location_uri': '',
                'version': '',
                'tags': [],
                'system_tags': [],
            },
        ],
    }
    app.post('/v1/items/batch/', json=payload)
    yield props
    for id in props['ids'].values():
        params = {'id': id}
        app.delete('/v1/item/', params=params)


@pytest.fixture(scope='function')
def test_collections() -> dict:
    props = [{
        'collection_name': generate_random_container_code(),
        'owner': 'user',
        'container_code': generate_random_container_code(),
        'id': str(uuid.uuid4()),
    }, {
        'collection_name': generate_random_container_code(),
        'owner': 'user',
        'container_code': generate_random_container_code(),
        'id': str(uuid.uuid4()),
    }]
    for i in range(0, len(props)):
        payload = {
            'id': props[i]['id'],
            'owner': props[i]['owner'],
            'container_code': props[i]['container_code'],
            'name': props[i]['collection_name']

        }
        app.post('/v1/collection/', json=payload)

    yield props
    for i in props:
        params = {'id': i['id']}
        app.delete('/v1/collection/', params=params)


@pytest.fixture(scope='function')
def test_attribute_template() -> str:
    payload = {
        'name': 'test_template',
        'project_code': 'test_project',
        'attributes': [
            {'name': 'attribute_1', 'optional': True, 'type': 'multiple_choice', 'options': ['val1', 'val2']}
        ],
    }
    response = app.post('/v1/template/', json=payload)
    attribute_template_id = loads(response.text)['result']['id']
    yield attribute_template_id
    params = {'id': attribute_template_id}
    app.delete('/v1/template/', params=params)
