from fastapi.testclient import TestClient

from app.main import app


class TestItems:
    app = TestClient(app)

    def test_01_get_item(self):
        response = self.app.get('/v1/item/')
        assert response.status_code == 200
        assert 'Placeholder' in response.text

    def test_02_create_item(self):
        response = self.app.post('/v1/item/')
        assert response.status_code == 200
        assert 'Placeholder' in response.text

    def test_03_update_item(self):
        response = self.app.put('/v1/item/')
        assert response.status_code == 200
        assert 'Placeholder' in response.text

    def test_04_trash_item(self):
        response = self.app.patch('/v1/item/')
        assert response.status_code == 200
        assert 'Placeholder' in response.text

    def test_05_delete_item(self):
        response = self.app.delete('/v1/item/')
        assert response.status_code == 200
        assert 'Placeholder' in response.text
