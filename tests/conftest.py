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

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

app = TestClient(app)

@pytest.fixture(scope='session')
def test_items():
    test_item_ids = {
        'name_folder': str(uuid.uuid4()),
        'folder': str(uuid.uuid4()),
        'file': str(uuid.uuid4()),
        'file_2': str(uuid.uuid4()),
        'file_3': str(uuid.uuid4()),
    }
    payload = {
        'items': [
            {
                'id': test_item_ids['name_folder'],
                'parent': None,
                'parent_path': None,
                'type': 'name_folder',
                'zone': 0,
                'name': 'user',
                'size': 0,
                'owner': 'user',
                'container_code': 'test_project',
                'container_type': 'project',
                'location_uri': '',
                'version': '',
            },
            {
                'id': test_item_ids['folder'],
                'parent': test_item_ids['name_folder'],
                'parent_path': 'user',
                'type': 'folder',
                'zone': 0,
                'name': 'test_folder',
                'size': 0,
                'owner': 'user',
                'container_code': 'test_project',
                'container_type': 'project',
                'location_uri': '',
                'version': '',
                'tags': [],
                'system_tags': [],
                'attribute_template_id': None,
                'attributes': {},
            },
            {
                'id': test_item_ids['file'],
                'parent': test_item_ids['folder'],
                'parent_path': 'user.test_folder',
                'type': 'file',
                'zone': 0,
                'name': 'test_file.txt',
                'size': 100,
                'owner': 'user',
                'container_code': 'test_project',
                'container_type': 'project',
                'location_uri': '',
                'version': '',
                'tags': [],
                'system_tags': [],
                'attribute_template_id': None,
                'attributes': {},
            },
            {
                'id': test_item_ids['file_2'],
                'parent': test_item_ids['folder'],
                'parent_path': 'user.test_folder',
                'type': 'file',
                'zone': 0,
                'name': 'test_file_2.txt',
                'size': 100,
                'owner': 'user',
                'container_code': 'test_project',
                'container_type': 'project',
                'location_uri': '',
                'version': '',
                'tags': [],
                'system_tags': [],
                'attribute_template_id': None,
                'attributes': {},
            },
            {
                'id': test_item_ids['file_3'],
                'parent': test_item_ids['folder'],
                'parent_path': 'user.test_folder',
                'type': 'file',
                'zone': 0,
                'name': 'test_file_3.txt',
                'size': 100,
                'owner': 'user',
                'container_code': 'test_project',
                'container_type': 'project',
                'location_uri': '',
                'version': '',
                'tags': [],
                'system_tags': [],
                'attribute_template_id': None,
                'attributes': {},
            },
        ],
    }
    app.post('/v1/items/batch/', json=payload)
    yield test_item_ids
    for id in test_item_ids.values():
        params = {'id': id}
        app.delete('/v1/item/', params=params)
