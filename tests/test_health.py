import unittest
from fastapi.testclient import TestClient
from main import app  # Make sure this imports your FastAPI app

client = TestClient(app)

class HealthCheckTest(unittest.TestCase):
    def test_test_endpoint(self):
        response = client.get("/test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "backend is up and running!"})
#OKAY