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

import re
import uuid
from json import loads

from fastapi.testclient import TestClient

from app.main import app

app = TestClient(app)


class TestItems:
    cleanup_item_ids = []

    @classmethod
    def teardown_class(cls):
        for id in cls.cleanup_item_ids:
            params = {'id': id}
            app.delete('/v1/item/', params=params)

    def test_get_item_by_id_200(self, test_items):
        response = app.get(f'/v1/item/{test_items["ids"]["file_1"]}/')
        assert response.status_code == 200

    def test_get_item_by_location_200(self):
        params = {
            'parent_path': 'user.test_folder',
            'name': 'test_file.txt',
            'archived': False,
            'zone': 0,
            'container_code': 'test_project',
            'recursive': False,
        }
        response = app.get('/v1/items/search/', params=params)
        assert response.status_code == 200

    def test_get_item_by_location_missing_zone_422(self):
        params = {
            'parent_path': 'user.test_folder',
            'name': 'test_file.txt',
            'archived': False,
            'container_code': 'test_project',
            'recursive': False,
        }
        response = app.get('/v1/item/search/', params=params)
        assert response.status_code == 422

    def test_get_items_by_id_batch_200(self, test_items):
        params = {'ids': [test_items['ids']['name_folder'], test_items['ids']['folder'], test_items['ids']['file_1']]}
        response = app.get('/v1/items/batch/', params=params)
        assert response.status_code == 200

    def test_create_item_200(self):
        item_id = str(uuid.uuid4())
        self.cleanup_item_ids.append(item_id)
        payload = {
            'id': item_id,
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'user.test_folder',
            'type': 'file',
            'zone': 0,
            'name': 'test_file.txt',
            'size': 0,
            'owner': 'admin',
            'container_code': 'create_item_200',
            'container_type': 'project',
            'location_uri': '',
            'version': '',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': {},
        }
        response = app.post('/v1/item/', json=payload)
        assert response.status_code == 200

    def test_create_items_batch_200(self):
        item_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        for id in item_ids:
            self.cleanup_item_ids.append(id)
        payload = {
            'items': [
                {
                    'id': item_ids[0],
                    'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                    'parent_path': 'user.folder',
                    'type': 'file',
                    'zone': 0,
                    'name': 'file_1.txt',
                    'size': 0,
                    'owner': 'user',
                    'container_code': 'create_items_batch',
                    'container_type': 'project',
                    'location_uri': '',
                    'version': '',
                    'tags': [],
                    'system_tags': [],
                    'attribute_template_id': None,
                    'attributes': {},
                },
                {
                    'id': item_ids[1],
                    'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                    'parent_path': 'user.folder',
                    'type': 'file',
                    'zone': 0,
                    'name': 'file_2.txt',
                    'size': 0,
                    'owner': 'user',
                    'container_code': 'create_items_batch',
                    'container_type': 'project',
                    'location_uri': '',
                    'version': '',
                    'tags': [],
                    'system_tags': [],
                    'attribute_template_id': None,
                    'attributes': {},
                },
            ]
        }
        response = app.post('/v1/items/batch/', json=payload)
        assert response.status_code == 200

    def test_create_item_wrong_type_422(self):
        payload = {
            'id': str(uuid.uuid4()),
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'user.test_folder',
            'type': 'invalid',
            'zone': 0,
            'name': 'test_file.txt',
            'size': 0,
            'owner': 'admin',
            'container_code': 'create_item_200',
            'container_type': 'project',
            'location_uri': '',
            'version': '',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': {},
        }
        response = app.post('/v1/item/', json=payload)
        assert response.status_code == 422

    def test_create_item_wrong_container_type_422(self):
        payload = {
            'id': str(uuid.uuid4()),
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'user.test_folder',
            'type': 'file',
            'zone': 0,
            'name': 'test_file.txt',
            'size': 0,
            'owner': 'admin',
            'container_code': 'create_item_200',
            'container_type': 'invalid',
            'location_uri': '',
            'version': '',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': {},
        }
        response = app.post('/v1/item/', json=payload)
        assert response.status_code == 422

    def test_create_name_folder_with_parent_422(self):
        payload = {
            'parent': str(uuid.uuid4()),
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
        }
        response = app.post('/v1/item/', json=payload)
        assert response.status_code == 422

    def test_update_item_200(self, test_items):
        params = {'id': test_items['ids']['file_1']}
        payload = {'name': 'test_file_updated.txt'}
        response = app.put('/v1/item/', json=payload, params=params)
        assert response.status_code == 200
        assert loads(response.text)['result']['name'] == 'test_file_updated.txt'

    def test_update_items_batch_200(self, test_items):
        params = {'ids': [test_items['ids']['name_folder'], test_items['ids']['folder'], test_items['ids']['file_1']]}
        payload = {'items': [{'owner': 'user_2'}, {'tags': ['update_items_batch']}, {'size': 500}]}
        response = app.put('/v1/items/batch/', params=params, json=payload)
        assert response.status_code == 200
        assert loads(response.text)['result'][0]['owner'] == 'user_2'
        assert loads(response.text)['result'][1]['extended']['extra']['tags'] == ['update_items_batch']
        assert loads(response.text)['result'][2]['size'] == 500

    def test_update_item_wrong_type_422(self, test_items):
        params = {'id': test_items['ids']['file_1']}
        payload = {'type': 'invalid'}
        response = app.put('/v1/item/', json=payload, params=params)
        assert response.status_code == 422

    def test_update_item_wrong_container_type_422(self, test_items):
        params = {'id': test_items['ids']['file_1']}
        payload = {'container_type': 'invalid'}
        response = app.put('/v1/item/', json=payload, params=params)
        assert response.status_code == 422

    def test_trash_item_200(self, test_items):
        params = {
            'id': test_items['ids']['file_1'],
            'archived': True,
        }
        response = app.patch('/v1/item/', params=params)
        assert response.status_code == 200
        assert loads(response.text)['result'][0]['archived'] == True

    def test_restore_item_200(self, test_items):
        params = {
            'id': test_items['ids']['file_1'],
            'archived': False,
        }
        response = app.patch('/v1/item/', params=params)
        assert response.status_code == 200
        assert loads(response.text)['result'][0]['archived'] == False

    def test_trash_folder_with_children_200(self, test_items):
        params = {
            'id': test_items['ids']['folder'],
            'archived': True,
        }
        response = app.patch('/v1/item/', params=params)
        assert response.status_code == 200
        assert len(loads(response.text)['result']) == 4
        for i in range(4):
            assert loads(response.text)['result'][i]['archived'] == True

    def test_restore_folder_with_children_200(self, test_items):
        params = {
            'id': test_items['ids']['folder'],
            'archived': False,
        }
        response = app.patch('/v1/item/', params=params)
        assert response.status_code == 200
        assert len(loads(response.text)['result']) == 4
        for i in range(4):
            assert loads(response.text)['result'][i]['archived'] == False

    def test_rename_item_on_conflict_200(self, test_items):
        params = {
            'id': test_items['ids']['file_1'],
            'archived': True,
        }
        app.patch('/v1/item/', params=params)
        item_id = str(uuid.uuid4())
        self.cleanup_item_ids.append(item_id)
        payload = {
            'id': item_id,
            'parent': test_items['ids']['folder'],
            'parent_path': 'user.test_folder',
            'type': 'file',
            'zone': 0,
            'name': 'test_file_1.txt',
            'size': 100,
            'owner': 'user',
            'container_code': test_items['container_code'],
            'container_type': 'project',
            'location_uri': '',
            'version': '',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': {},
        }
        app.post('/v1/item/', json=payload)
        params = {
            'id': test_items['ids']['file_1'],
            'archived': False,
        }
        response = app.patch('/v1/item/', params=params)
        assert response.status_code == 200
        regex = '_\d{10}'
        assert re.search(regex, loads(response.text)['result'][0]['name'])

    def test_delete_item_200(self, test_items):
        params = {'id': test_items['ids']['file_1']}
        response = app.delete('/v1/item/', params=params)
        assert response.status_code == 200

    def test_delete_items_by_id_batch_200(self, test_items):
        params = {'ids': [test_items['ids']['file_2'], test_items['ids']['file_3']]}
        response = app.delete('/v1/items/batch/', params=params)
        assert response.status_code == 200
