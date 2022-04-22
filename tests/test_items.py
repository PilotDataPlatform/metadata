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

from json import loads

import pytest
from fastapi.testclient import TestClient

from app.main import app

reused_item_ids = []
reused_container_code = 'test_container'


class TestItems:
    app = TestClient(app)

    @pytest.mark.dependency(name='test_01')
    def test_create_item_200(self):
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'file',
            'size': 0,
            'owner': 'admin',
            'container_code': reused_container_code,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': {},
        }
        response = self.app.post('/v1/item/', json=payload)
        global reused_item_ids
        reused_item_ids.append(loads(response.text)['result']['id'])
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_get_item_by_id_200(self):
        response = self.app.get(f'/v1/item/{reused_item_ids[0]}/')
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_get_item_by_location_200(self):
        params = {
            'parent_path': 'folder1.folder2',
            'archived': False,
            'zone': 0,
            'container_code': reused_container_code,
            'recursive': False,
        }
        response = self.app.get('/v1/items/search/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_update_item_200(self):
        params = {'id': reused_item_ids[0]}
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'file_renamed',
            'size': 0,
            'owner': 'admin',
            'container_code': reused_container_code,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': {},
        }
        response = self.app.put('/v1/item/', json=payload, params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_trash_item_200(self):
        params = {
            'id': reused_item_ids[0],
            'archived': True,
        }
        response = self.app.patch('/v1/item/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_restore_item_200(self):
        params = {
            'id': reused_item_ids[0],
            'archived': False,
        }
        response = self.app.patch('/v1/item/', params=params)
        assert response.status_code == 200

    def test_get_item_by_location_missing_zone_422(self):
        params = {
            'parent_path': 'folder1.folder2',
            'archived': False,
            'container_code': reused_container_code,
            'recursive': False,
        }
        response = self.app.get('/v1/item/search/', params=params)
        assert response.status_code == 422

    def test_create_item_wrong_type_422(self):
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'folder1.folder2',
            'type': 'invalid',
            'zone': 0,
            'name': 'file',
            'size': 0,
            'owner': 'admin',
            'container_code': reused_container_code,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': None,
        }
        response = self.app.post('/v1/item/', json=payload)
        assert response.status_code == 422

    def test_create_item_wrong_container_type_422(self):
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'file',
            'size': 0,
            'owner': 'admin',
            'container_code': reused_container_code,
            'container_type': 'invalid',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': None,
        }
        response = self.app.post('/v1/item/', json=payload)
        assert response.status_code == 422

    @pytest.mark.dependency(depends=['test_01'])
    def test_update_item_wrong_type_422(self):
        params = {'id': reused_item_ids[0]}
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'folder1.folder2',
            'type': 'invalid',
            'zone': 0,
            'name': 'file_renamed',
            'size': 0,
            'owner': 'admin',
            'container_code': reused_container_code,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': None,
        }
        response = self.app.put('/v1/item/', json=payload, params=params)
        assert response.status_code == 422

    @pytest.mark.dependency(depends=['test_01'])
    def test_update_item_wrong_container_type_422(self):
        params = {'id': reused_item_ids[0]}
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'file_renamed',
            'size': 0,
            'owner': 'admin',
            'container_code': reused_container_code,
            'container_type': 'invalid',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': None,
        }
        response = self.app.put('/v1/item/', json=payload, params=params)
        assert response.status_code == 422

    def test_rename_item_on_conflict_200(self):
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'conflict',
            'size': 0,
            'owner': 'admin',
            'container_code': reused_container_code,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': {},
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
            'parent_path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'conflict',
            'size': 0,
            'owner': 'admin',
            'container_code': reused_container_code,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': {},
        }
        response = self.app.post('/v1/item/', json=payload)
        item_2_id = loads(response.text)['result']['id']
        params = {
            'id': item_1_id,
            'archived': False,
        }
        response = self.app.patch('/v1/item/', params=params)
        assert response.status_code == 200
        assert '_' in loads(response.text)['result']['name']
        params = {'id': item_1_id}
        self.app.delete('/v1/item', params=params)
        params = {'id': item_2_id}
        self.app.delete('/v1/item', params=params)

    @pytest.mark.dependency(depends=['test_01'])
    def test_delete_item_200(self):
        params = {'id': reused_item_ids[0]}
        response = self.app.delete('/v1/item/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(name='test_14')
    def test_create_items_batch_200(self):
        payload = {
            'items': [
                {
                    'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                    'parent_path': 'folder1.folder2',
                    'type': 'file',
                    'zone': 0,
                    'name': 'file_1',
                    'size': 0,
                    'owner': 'admin',
                    'container_code': reused_container_code,
                    'container_type': 'project',
                    'location_uri': 'https://example.com',
                    'version': '1.0',
                    'tags': [],
                    'system_tags': [],
                    'attribute_template_id': None,
                    'attributes': {},
                },
                {
                    'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                    'parent_path': 'folder1.folder2',
                    'type': 'file',
                    'zone': 0,
                    'name': 'file_2',
                    'size': 0,
                    'owner': 'admin',
                    'container_code': reused_container_code,
                    'container_type': 'project',
                    'location_uri': 'https://example.com',
                    'version': '1.0',
                    'tags': [],
                    'system_tags': [],
                    'attribute_template_id': None,
                    'attributes': {},
                },
            ]
        }
        response = self.app.post('/v1/items/batch/', json=payload)
        global reused_item_ids
        reused_item_ids.append(loads(response.text)['result'][0]['id'])
        reused_item_ids.append(loads(response.text)['result'][1]['id'])
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_14'])
    def test_get_items_by_id_batch_200(self):
        params = {'ids': [reused_item_ids[1], reused_item_ids[2]]}
        response = self.app.get('/v1/items/batch/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_14'])
    def test_update_items_batch_200(self):
        params = {'ids': [reused_item_ids[1], reused_item_ids[2]]}
        payload = {
            'items': [
                {
                    'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                    'parent_path': 'folder1.folder2.folder3',
                    'type': 'file',
                    'zone': 0,
                    'name': 'file_1',
                    'size': 0,
                    'owner': 'admin',
                    'container_code': reused_container_code,
                    'container_type': 'project',
                    'location_uri': 'https://example.com',
                    'version': '1.0',
                    'tags': [],
                    'system_tags': [],
                    'attribute_template_id': None,
                    'attributes': {},
                },
                {
                    'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                    'parent_path': 'folder1.folder2.folder3',
                    'type': 'file',
                    'zone': 0,
                    'name': 'file_2',
                    'size': 0,
                    'owner': 'admin',
                    'container_code': reused_container_code,
                    'container_type': 'project',
                    'location_uri': 'https://example.com',
                    'version': '1.0',
                    'tags': [],
                    'system_tags': [],
                    'attribute_template_id': None,
                    'attributes': {},
                },
            ]
        }
        response = self.app.put('/v1/items/batch/', params=params, json=payload)
        assert response.status_code == 200
        assert loads(response.text)['result'][0]['parent_path'] == 'folder1.folder2.folder3'

    @pytest.mark.dependency(depends=['test_14'])
    def test_delete_items_by_id_batch_200(self):
        params = {'ids': [reused_item_ids[1], reused_item_ids[2]]}
        response = self.app.delete('/v1/items/batch/', params=params)
        assert response.status_code == 200

    def test_create_name_folder_with_parent_422(self):
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'parent_path': 'folder1.folder2',
            'type': 'name_folder',
            'zone': 0,
            'name': 'file',
            'size': 0,
            'owner': 'admin',
            'container_code': reused_container_code,
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'tags': [],
            'system_tags': [],
            'attribute_template_id': None,
            'attributes': {},
        }
        response = self.app.post('/v1/item/', json=payload)
        assert response.status_code == 422
