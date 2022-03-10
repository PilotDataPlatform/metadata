from fastapi.testclient import TestClient

from app.main import app


class TestAttributeTemplates:
    app = TestClient(app)

    def test_01_get_attribute_template(self):
        response = self.app.get('/v1/template/')
        assert response.status_code == 200
        assert 'Placeholder' in response.text

    def test_02_create_attribute_template(self):
        response = self.app.post('/v1/template/')
        assert response.status_code == 200
        assert 'Placeholder' in response.text

    def test_03_update_attribute_template(self):
        response = self.app.put('/v1/template/')
        assert response.status_code == 200
        assert 'Placeholder' in response.text

    def test_04_delete_attribute_template(self):
        response = self.app.delete('/v1/template/')
        assert response.status_code == 200
        assert 'Placeholder' in response.text
