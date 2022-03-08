from fastapi.testclient import TestClient

from app.main import app

# This file is for early testing only
# Delete when a functional endpoint is added


class TestAnnouncement:
    app = TestClient(app)

    def test_01_hello_world(self):
        response = self.app.get('/v1/hello-world/')
        assert response.status_code == 200
        assert 'Hello world' in response.text
