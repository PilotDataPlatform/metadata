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
from json import loads

import pytest
from fastapi.testclient import TestClient

from app.main import app

reused_item_id = None
reused_container = str(uuid.uuid4())


class TestItems:
    app = TestClient(app)

    @pytest.mark.dependency(name='test_01')
    def test_01_create_item(self):
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'file',
            'size': 0,
            'owner': 'admin',
            'container': reused_container,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'extra': {},
        }
        response = self.app.post('/v1/item/', json=payload)
        print(response.text)
        global reused_item_id
        reused_item_id = loads(response.text)['result']['id']
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_02_get_item_by_id(self):
        params = {'id': reused_item_id}
        response = self.app.get('/v1/item/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_03_get_item_by_location(self):
        params = {
            'path': 'folder1.folder2',
            'archived': False,
            'zone': 0,
            'container': reused_container,
        }
        response = self.app.get('/v1/item/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_04_update_item(self):
        params = {'id': reused_item_id}
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'file_renamed',
            'size': 0,
            'owner': 'admin',
            'container': reused_container,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'extra': {},
        }
        response = self.app.put('/v1/item/', json=payload, params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_05_trash_item(self):
        params = {
            'id': reused_item_id,
            'archived': True,
        }
        response = self.app.patch('/v1/item/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_06_restore_item(self):
        params = {
            'id': reused_item_id,
            'archived': False,
        }
        response = self.app.patch('/v1/item/', params=params)
        assert response.status_code == 200

    def test_07_get_item_by_location_missing_params(self):
        params = {
            'path': 'folder1.folder2',
            'archived': False,
            'container': reused_container,
        }
        response = self.app.get('/v1/item/', params=params)
        assert response.status_code == 400

    def test_08_create_item_wrong_type(self):
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'path': 'folder1.folder2',
            'type': 'invalid',
            'zone': 0,
            'name': 'file',
            'size': 0,
            'owner': 'admin',
            'container': reused_container,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'extra': {},
        }
        response = self.app.post('/v1/item/', json=payload)
        assert response.status_code == 422

    def test_09_create_item_wrong_container_type(self):
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'file',
            'size': 0,
            'owner': 'admin',
            'container': reused_container,
            'container_type': 'invalid',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'extra': {},
        }
        response = self.app.post('/v1/item/', json=payload)
        assert response.status_code == 422

    @pytest.mark.dependency(depends=['test_01'])
    def test_10_update_item_wrong_type(self):
        params = {'id': reused_item_id}
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'path': 'folder1.folder2',
            'type': 'invalid',
            'zone': 0,
            'name': 'file_renamed',
            'size': 0,
            'owner': 'admin',
            'container': reused_container,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'extra': {},
        }
        response = self.app.put('/v1/item/', json=payload, params=params)
        assert response.status_code == 422

    @pytest.mark.dependency(depends=['test_01'])
    def test_11_update_item_wrong_container_type(self):
        params = {'id': reused_item_id}
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'file_renamed',
            'size': 0,
            'owner': 'admin',
            'container': reused_container,
            'container_type': 'invalid',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'extra': {},
        }
        response = self.app.put('/v1/item/', json=payload, params=params)
        assert response.status_code == 422

    def test_12_rename_item_on_conflict(self):
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'conflict',
            'size': 0,
            'owner': 'admin',
            'container': reused_container,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'extra': {},
        }
        response = self.app.post('/v1/item/', json=payload)
        item_1_id = loads(response.text)['result']['id']
        params = {
            'id': item_1_id,
            'archived': True,
        }
        self.app.patch('/v1/item/', params=params)
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'conflict',
            'size': 0,
            'owner': 'admin',
            'container': reused_container,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'extra': {},
        }
        response = self.app.post('/v1/item/', json=payload)
        item_2_id = loads(response.text)['result']['id']
        params = {
            'id': item_1_id,
            'archived': False,
        }
        response = self.app.patch('/v1/item/', params=params)
        assert loads(response.text)['result']['name'] == 'conflict_copy'
        assert str(loads(response.text)['result']['path']) == 'folder1.folder2.conflict_copy'
        params = {'id': item_1_id}
        self.app.delete('/v1/item/', params=params)
        params = {'id': item_2_id}
        self.app.delete('/v1/item/', params=params)

    @pytest.mark.dependency(depends=['test_01'])
    def test_13_delete_item(self):
        params = {'id': reused_item_id}
        response = self.app.delete('/v1/item/', params=params)
        assert response.status_code == 200
