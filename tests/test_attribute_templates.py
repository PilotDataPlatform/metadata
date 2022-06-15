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

from fastapi.testclient import TestClient

from app.main import app

app = TestClient(app)


class TestAttributeTemplates:
    def test_get_attribute_template_by_id_200(self, test_attribute_template):
        response = app.get(f'/v1/template/{test_attribute_template}')
        assert response.status_code == 200

    def test_get_attribute_template_by_project_code_200(self, test_attribute_template):
        params = {'project_code': 'test_project'}
        response = app.get('/v1/template/', params=params)
        assert response.status_code == 200

    def test_get_attribute_template_by_project_code_and_name_200(self, test_attribute_template):
        params = {'project_code': 'test_project', 'name': 'test_template'}
        response = app.get('/v1/template/', params=params)
        res = response.json()['result'][0]
        assert response.status_code == 200
        assert res['name'] == 'test_template'
        assert res['project_code'] == 'test_project'

    def test_get_attribute_template_by_project_code_and_invalid_name_200(self, test_attribute_template):
        params = {'project_code': 'test_project', 'name': 'invalid_name'}
        response = app.get('/v1/template/', params=params)
        res = response.json()['result']
        assert response.status_code == 200
        assert res == []

    def test_create_attribute_template_200(self):
        payload = {
            'name': 'template_1',
            'project_code': 'test_project',
            'attributes': [
                {'name': 'attribute_1', 'optional': True, 'type': 'multiple_choice', 'options': ['val1', 'val2']}
            ],
        }
        response = app.post('/v1/template/', json=payload)
        assert response.status_code == 200

    def test_create_attribute_template_wrong_type_422(self):
        payload = {
            'name': 'template_1',
            'project_code': 'test_project',
            'attributes': [{'name': 'attribute_1', 'optional': True, 'type': 'invalid', 'options': 'val1, val2'}],
        }
        response = app.post('/v1/template/', json=payload)
        assert response.status_code == 422

    def test_update_attribute_template_200(self, test_attribute_template):
        params = {'id': test_attribute_template}
        payload = {
            'name': 'template_1',
            'project_code': 'test_project',
            'attributes': [
                {'name': 'attribute_1', 'optional': True, 'type': 'multiple_choice', 'options': ['val1', 'val2']},
                {'name': 'attribute_2', 'optional': True, 'type': 'text', 'options': []},
            ],
        }
        response = app.put('/v1/template/', json=payload, params=params)
        assert response.status_code == 200
        assert len(loads(response.text)['result']['attributes']) == 2

    def test_delete_attribute_template_200(self, test_attribute_template):
        params = {'id': test_attribute_template}
        response = app.delete('/v1/template/', params=params)
        assert response.status_code == 200
