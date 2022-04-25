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

reused_template_id = None
reused_project_code = 'project0422'


class TestAttributeTemplates:
    app = TestClient(app)

    @pytest.mark.dependency(name='test_01')
    def test_create_attribute_template_200(self):
        payload = {
            'name': 'template_1',
            'project_code': reused_project_code,
            'attributes': [
                {'name': 'attribute_1', 'optional': True, 'type': 'multiple_choice', 'options': ['val1', 'val2']}
            ],
        }
        response = self.app.post('/v1/template/', json=payload)
        global reused_template_id
        reused_template_id = loads(response.text)['result']['id']
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_get_attribute_template_by_id_200(self):
        response = self.app.get(f'/v1/template/{reused_template_id}')
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_get_attribute_template_by_project_code_200(self):
        params = {'project_code': reused_project_code}
        response = self.app.get('/v1/template/', params=params)
        assert response.status_code == 200

    @pytest.mark.dependency(depends=['test_01'])
    def test_update_attribute_template_200(self):
        params = {'id': reused_template_id}
        payload = {
            'name': 'template_1',
            'project_code': reused_project_code,
            'attributes': [
                {'name': 'attribute_1', 'optional': True, 'type': 'multiple_choice', 'options': ['val1', 'val2']},
                {'name': 'attribute_2', 'optional': True, 'type': 'text', 'options': []},
            ],
        }
        response = self.app.put('/v1/template/', json=payload, params=params)
        assert response.status_code == 200
        assert len(loads(response.text)['result']['attributes']) == 2

    @pytest.mark.dependency(depends=['test_01'])
    def test_delete_attribute_template_200(self):
        params = {'id': reused_template_id}
        response = self.app.delete('/v1/template/', params=params)
        assert response.status_code == 200

    def test_create_attribute_template_wrong_type_422(self):
        payload = {
            'name': 'template_1',
            'project_code': reused_project_code,
            'attributes': [{'name': 'attribute_1', 'optional': True, 'type': 'invalid', 'options': 'val1, val2'}],
        }
        response = self.app.post('/v1/template/', json=payload)
        assert response.status_code == 422
