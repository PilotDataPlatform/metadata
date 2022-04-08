from json import loads

import pytest
from fastapi.testclient import TestClient

from app.main import app

reused_template_id = None
reused_project_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'


class TestAttributeTemplates:
    app = TestClient(app)

    @pytest.mark.dependency(name='test_01')
    def test_01_create_attribute_template(self):
        payload = {
            'name': 'template_1',
            'project_id': reused_project_id,
            'attributes': [
                {'name': 'attribute_1', 'optional': True, 'type': 'multiple_choice', 'options': ['val1', 'val2']}
            ],
        }
        response = self.app.post('/v1/template/', json=payload)
        global reused_template_id
        reused_template_id = loads(response.text)['result']['id']
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_02_get_attribute_template_by_id(self):
        response = self.app.get(f'/v1/template/{reused_template_id}')
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_03_get_attribute_template_by_project_id(self):
        params = {'project_id': reused_project_id}
        response = self.app.get('/v1/template/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_04_update_attribute_template(self):
        params = {'id': reused_template_id}
        payload = {
            'name': 'template_1',
            'project_id': reused_project_id,
            'attributes': [
                {'name': 'attribute_1', 'optional': True, 'type': 'multiple_choice', 'options': ['val1', 'val2']},
                {'name': 'attribute_2', 'optional': True, 'type': 'text', 'options': []},
            ],
        }
        response = self.app.put('/v1/template/', json=payload, params=params)
        assert response.status_code == 200
        assert len(loads(response.text)['result']['attributes']) == 2

    @pytest.mark.dependency(depends=['test_01'])
    def test_05_delete_attribute_template(self):
        params = {'id': reused_template_id}
        response = self.app.delete('/v1/template/', params=params)
        assert response.status_code == 200

    def test_06_create_attribute_template_wrong_type(self):
        payload = {
            'name': 'template_1',
            'project_id': reused_project_id,
            'attributes': [{'name': 'attribute_1', 'optional': True, 'type': 'invalid', 'options': 'val1, val2'}],
        }
        response = self.app.post('/v1/template/', json=payload)
        assert response.status_code == 422
