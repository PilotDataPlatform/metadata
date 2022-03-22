from json import loads

import pytest
from fastapi.testclient import TestClient

from app.main import app

item_id = None


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
            'container': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'container_type': 'project',
            'location_uri': 'https://example.com',
            'version': '1.0',
            'extra': {},
        }
        response = self.app.post('/v1/item/', json=payload)
        global item_id
        item_id = loads(response.text)['result']['id']
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_02_get_item_by_id(self):
        params = {'id': item_id}
        response = self.app.get('/v1/item/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_03_get_item_by_location(self):
        params = {
            'path': 'folder1.folder2',
            'archived': False,
            'zone': 0,
            'container': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        }
        response = self.app.get('/v1/item/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_04_update_item(self):
        params = {'id': item_id}
        payload = {
            'parent': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            'path': 'folder1.folder2',
            'type': 'file',
            'zone': 0,
            'name': 'file_renamed',
            'size': 0,
            'owner': 'admin',
            'container': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
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
            'id': item_id,
            'archived': True,
        }
        response = self.app.patch('/v1/item/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_06_delete_item(self):
        params = {'id': item_id}
        response = self.app.delete('/v1/item/', params=params)
        assert response.status_code == 200
