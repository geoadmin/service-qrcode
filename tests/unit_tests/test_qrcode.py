import unittest

from app import app
from app.version import APP_VERSION


class QrCodeTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.assertEqual(app.debug, False)
        self.route_prefix = "/v4/qrcode"
        self.valid_origin_header = {
            # see .env.test
            'Origin': 'some_random_domain'
        }

    def tearDown(self):
        pass

    def test_checker(self):
        response = self.app.get(f"{self.route_prefix}/checker", headers=self.valid_origin_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json, {"message": "OK", "success": True, "version": APP_VERSION})

    def test_generate_errors(self):
        response = self.app.get(f"{self.route_prefix}/generate")
        self.assertEqual(response.status_code, 403, msg="ORIGIN must be set")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json, {
                "error": {
                    "code": 403, "message": "Not allowed"
                }, "success": False
            }
        )
        response = self.app.post(f"{self.route_prefix}/generate", headers=self.valid_origin_header)
        self.assertEqual(response.status_code, 405, msg="POST method is not allowed")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json,
            {
                "error":
                    {
                        "code": 405, "message": "The method is not allowed for the requested URL."
                    },
                "success": False
            }
        )

        response = self.app.get(f"{self.route_prefix}/generate", headers=self.valid_origin_header)
        self.assertEqual(
            response.status_code, 400, msg="Should respond with a 400 when URL param is missing"
        )
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json, {
                "error": {
                    "code": 400, "message": "Missing parameter 'url'"
                }, "success": False
            }
        )

    def test_generate_domain_restriction(self):
        response = self.app.get(
            f"{self.route_prefix}/generate?url=https://some_random_domain/test",
            content_type="application/json",
            headers=self.valid_origin_header
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], "some_random_domain")
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], "GET, POST, OPTIONS")

        response = self.app.get(
            f"{self.route_prefix}/generate?url=https://www.example.com/test",
            content_type="application/json",
            headers=self.valid_origin_header
        )
        self.assertEqual(response.status_code, 400, msg="Domain restriction not applied")
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], "some_random_domain")
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], "GET, POST, OPTIONS")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json, {
                "error": {
                    "code": 400, "message": "URL domain not allowed"
                }, "success": False
            }
        )

        response = self.app.get(
            f"{self.route_prefix}/generate?url=https://www.example.com/test",
            content_type="application/json",
            headers={"Origin": "www.example.com"}
        )
        self.assertEqual(response.status_code, 403, msg="Domain restriction not applied")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json, {
                "error": {
                    "code": 403, "message": "Not allowed"
                }, "success": False
            }
        )
