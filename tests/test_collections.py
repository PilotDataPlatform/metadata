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

from fastapi.testclient import TestClient

from app.config import ConfigClass
from app.main import app

app = TestClient(app)


def generate_random_container_code() -> str:
    random_container_code = 'test_'
    for _ in range(8):
        random_container_code += chr(random.randint(32, 126))
    return random_container_code


class TestItems:
    cleanup_item_ids = []

    @classmethod
    def teardown_class(cls):
        for id in cls.cleanup_item_ids:
            params = {'id': id}
            app.delete('/v1/collection/', params=params)

    def test_get_collection_200(self, test_collections):
        param = {'owner': test_collections[0]['owner'], 'container_code': test_collections[0]['container_code']}
        response = app.get('/v1/collection/search/', params=param)
        res = response.json()['result'][0]
        assert response.status_code == 200
        assert res['name'] == test_collections[0]['collection_name']

    def test_get_collection_with_invalid_sorting_404(self, test_collections):
        param = {'owner': test_collections[0]['owner'], 'container_code': test_collections[0]['container_code'],
                 'sorting': 'created_time_x'}
        response = app.get('/v1/collection/search/', params=param)
        assert response.status_code == 404

    def test_get_collection_by_id_200(self, test_collections):
        response = app.get(f'/v1/collection/{test_collections[0]["id"]}/')
        res = response.json()['result']
        assert response.status_code == 200
        assert res['name'] == test_collections[0]['collection_name']

    def test_delete_collection_200(self, test_collections):
        param = {'id': test_collections[0]['id']}
        response = app.delete('/v1/collection/', params=param)
        assert response.status_code == 200

    def test_create_collection_200(self):
        collection_id = str(uuid.uuid4())
        self.cleanup_item_ids.append(collection_id)
        payload = {
            'id': collection_id,
            'owner': 'owner',
            'container_code': 'testproject',
            'name': 'collectiontest'
        }
        response = app.post('/v1/collection/', json=payload)
        assert response.status_code == 200

    def test_create_collection_over_limit_400(self):
        for _i in range(0, ConfigClass.MAX_COLLECTIONS):
            collection_id = str(uuid.uuid4())
            self.cleanup_item_ids.append(collection_id)
            payload = {
                'id': collection_id,
                'owner': 'owner',
                'container_code': 'testproject',
                'name': generate_random_container_code()
            }
            app.post('/v1/collection/', json=payload)

        collection_id = str(uuid.uuid4())
        self.cleanup_item_ids.append(collection_id)
        payload = {
            'id': collection_id,
            'owner': 'owner',
            'container_code': 'testproject',
            'name': generate_random_container_code()
        }

        response = app.post('/v1/collection/', json=payload)
        res = response.json()['error_msg']
        assert response.status_code == 400
        assert f'Cannot create more than {ConfigClass.MAX_COLLECTIONS} collections' in res

    def test_create_collection_name_already_exists_400(self, test_collections):
        collection_id = str(uuid.uuid4())
        collection_name = test_collections[0]['collection_name']
        self.cleanup_item_ids.append(collection_id)
        payload = {
            'id': collection_id,
            'owner': test_collections[0]['owner'],
            'container_code': test_collections[0]['container_code'],
            'name': test_collections[0]['collection_name']
        }

        response = app.post('/v1/collection/', json=payload)
        res = response.json()['error_msg']
        assert response.status_code == 400
        assert f'Collection {collection_name} already exists' in res

    def test_update_collection_name_200(self, test_collections):
        payload = {
            'owner': test_collections[0]['owner'],
            'container_code': test_collections[0]['container_code'],
            'collections': [
                {
                    'id': test_collections[0]['id'],
                    'name': 'updatedcollection'
                }
            ]
        }
        response = app.put('/v1/collection/', json=payload)
        assert response.status_code == 200

    def test_update_collection_with_duplicate_name_in_payload_422(self):
        payload = {
            'owner': 'owner',
            'container_code': 'code',
            'collections': [
                {
                    'id': str(uuid.uuid4()),
                    'name': 'duplicatename'
                },

                {
                    'id': str(uuid.uuid4()),
                    'name': 'duplicatename'
                }
            ]
        }
        response = app.put('/v1/collection/', json=payload)
        assert response.status_code == 422

    def test_update_collection_with_name_already_exists_400(self, test_collections):
        name_exists = [test_collections[0]['collection_name']]
        payload = {
            'owner': test_collections[0]['owner'],
            'container_code': test_collections[0]['container_code'],
            'collections': [
                {
                    'id': test_collections[0]['id'],
                    'name': test_collections[0]['collection_name']
                }
            ]
        }
        response = app.put('/v1/collection/', json=payload)
        res = response.json()['error_msg']
        assert response.status_code == 400
        assert f'Collection name(s) {name_exists} already exists' in res

    def test_update_collection_name_with_non_existent_id_400(self, test_collections):
        id_not_exist = ['c8e7a842-2f96-4cbe-9f5b-d67ba86132ad']
        payload = {
            'owner': test_collections[0]['owner'],
            'container_code': test_collections[0]['container_code'],
            'collections': [
                {
                    'id': test_collections[0]['id'],
                    'name': 'name1'
                },

                {
                    'id': id_not_exist[0],
                    'name': 'name2'
                }
            ]
        }
        response = app.put('/v1/collection/', json=payload)
        res = response.json()['error_msg']
        assert response.status_code == 400
        assert f'Collection id(s) {id_not_exist} do not exist' in res

    def test_get_collection_items_archived_false_200(self, test_collections, test_items):
        # add items
        payload = {
            'id': test_collections[0]['id'],
            'item_ids': [
                test_items['ids']['file_1'], test_items['ids']['file_2']
            ]
        }
        app.post('/v1/collection/items/', json=payload)

        # archive item
        trash_payload = {'id': test_items['ids']['file_1'], 'archived': True}
        app.patch('/v1/item/', params=trash_payload)

        # get item
        params = {'id': test_collections[0]['id']}
        response = app.get('/v1/collection/items/', params=params)
        res = response.json()['result']
        assert response.status_code == 200
        assert len(res) == 1
        assert res[0]['name'] == 'test_file_2.txt'
        assert res[0]['archived'] is False

    def test_get_collection_items_archived_true_200(self, test_collections, test_items):
        # add items
        payload = {
            'id': test_collections[0]['id'],
            'item_ids': [
                test_items['ids']['file_1'], test_items['ids']['file_2']
            ]
        }
        app.post('/v1/collection/items/', json=payload)

        # archive item
        trash_payload = {'id': test_items['ids']['file_2'], 'archived': True}
        app.patch('/v1/item/', params=trash_payload)

        # get item
        params = {'id': test_collections[0]['id'], 'archived': True}
        response = app.get('/v1/collection/items/', params=params)
        res = response.json()['result']
        assert response.status_code == 200
        assert len(res) == 1
        assert res[0]['name'] == 'test_file_2.txt'
        assert res[0]['archived'] is True

    def test_add_collection_items_200(self, test_collections, test_items):
        # add items
        payload = {
            'id': test_collections[0]['id'],
            'item_ids': [
                test_items['ids']['file_1'], test_items['ids']['file_2']
            ]
        }
        response = app.post('/v1/collection/items/', json=payload)
        res = response.json()['result']
        assert response.status_code == 200
        assert res['item_ids'][0] == test_items['ids']['file_1']
        assert res['item_ids'][1] == test_items['ids']['file_2']

    def test_remove_collection_items_200(self, test_collections, test_items):
        # add items
        payload = {
            'id': test_collections[0]['id'],
            'item_ids': [
                test_items['ids']['file_1'], test_items['ids']['file_2']
            ]
        }
        app.post('/v1/collection/items/', json=payload)

        # remove items
        params = {'id': test_collections[0]['id'], 'item_ids': [test_items['ids']['file_1'],
                                                                test_items['ids']['file_2']]}
        response = app.delete('/v1/collection/items/', json=params)
        assert response.status_code == 200
