import time
import unittest
from unittest.mock import patch
from flask_testing import TestCase
from app import app, cache, limiter
from config import Config

class TestConfig(Config):
    TESTING = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 10  # Set a longer timeout for testing reliability
    RATELIMIT_ENABLED = True


class FlaskAppTestCase(TestCase):
    def create_app(self):
        app.config.from_object(TestConfig)
        cache.init_app(app)
        limiter.init_app(app)  # Re-initialize limiter with test config
        return app

    def setUp(self):
        cache.clear()  # Clear cache before each test

    def tearDown(self):
        pass
    
    def test_home_endpoint(self):
        resp = self.client.get('/')
        self.assert200(resp)
        data = resp.get_json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Hello from flask App v4!")
      
    def test_health_endpoint(self):
        resp = self.client.get('/health')
        self.assert200(resp)
        self.assertEqual(resp.get_json()["status"], "OK")

    @patch('app.time.sleep')
    def test_heavy_endpoint(self, mock_sleep):
        resp = self.client.get('/heavy')
        self.assert200(resp)
        self.assertEqual(resp.get_json()["message"], "Heavy Configuration done!")
        # Assert that the mocked sleep was correctly called with 65 seconds
        mock_sleep.assert_called_once_with(65)

    def test_cacheme_endpoint(self):
        resp1 = self.client.get('/cacheme/test_param')
        self.assert200(resp1)
        data1 = resp1.get_json()
        self.assertEqual(data1["message"], "Hello, test_param!")
        
        resp2 = self.client.get('/cacheme/test_param')
        self.assert200(resp2)
        data2 = resp2.get_json()
        self.assertEqual(data1["random"], data2["random"])

        cache.clear()
        resp3 = self.client.get('/cacheme/test_param')
        self.assert200(resp3)
        data3 = resp3.get_json()
        self.assertNotEqual(data1["random"], data3["random"])

    def test_error_endpoint(self):
        resp = self.client.get('/error')
        self.assertEqual(resp.status_code, 500)
        data = resp.get_json()
        self.assertEqual(data["error"], "An internal error occurred")

    def test_bigjson_endpoint(self):
        resp = self.client.get('/bigjson')
        self.assert200(resp)
        data = resp.get_json()
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 1000)

    def test_api_rate_limit_endpoint(self):
        for _ in range(5):
            resp = self.client.get('/api')
            self.assert200(resp)
            
        # The 6th request inside a minute should hit the rate limiter and throw 429
        resp = self.client.get('/api')
        self.assertEqual(resp.status_code, 429)

if __name__ == '__main__':
    unittest.main()