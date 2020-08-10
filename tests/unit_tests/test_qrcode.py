import unittest
import json

from app import app


class QrCodeTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.assertEqual(app.debug, False)
        self.route_prefix = "/v4/qrcode"

    def tearDown(self):
        pass

    def test_api_version(self):
        response = self.app.get("/v3/qrcode/checker", headers={"Origin": "map.geo.admin.ch"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json, {
                "error": {
                    "code": 400, "message": "api version v3 not supported"
                }, "success": False
            }
        )

        response = self.app.get("/v4/qrcode/checker", headers={"Origin": "map.geo.admin.ch"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/v3/qrcode/generate", headers={"Origin": "map.geo.admin.ch"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json, {
                "error": {
                    "code": 400, "message": "api version v3 not supported"
                }, "success": False
            }
        )

    def test_checker(self):
        response = self.app.get(
            f"{self.route_prefix}/checker", headers={"Origin": "map.geo.admin.ch"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json, {"message": "OK", "success": True})

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
        response = self.app.get(
            f"{self.route_prefix}/generate", headers={"Origin": "map.geo.admin.ch"}
        )
        self.assertEqual(response.status_code, 405, msg="GET method is not allowed")
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

        response = self.app.post(
            f"{self.route_prefix}/generate", headers={"Origin": "map.geo.admin.ch"}
        )
        self.assertEqual(response.status_code, 400, msg="JSON body is requested")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json,
            {
                "error":
                    {
                        "code": 400,
                        "message": "The property 'url' is missing from the request body"
                    },
                "success": False
            }
        )

        response = self.app.post(
            f"{self.route_prefix}/generate",
            data=json.dumps({"url": "https://example.com"}),
            content_type="text/html",
            headers={"Origin": "map.geo.admin.ch"}
        )
        self.assertEqual(response.status_code, 400, msg="Only JSON body is accepted")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json,
            {
                "error":
                    {
                        "code": 400,
                        "message": "The property 'url' is missing from the request body"
                    },
                "success": False
            }
        )

    def test_generate_domain_restriction(self):
        response = self.app.post(
            f"{self.route_prefix}/generate",
            data=json.dumps({"url": "https://map.geo.admin.ch/test"}),
            content_type="application/json",
            headers={"Origin": "map.geo.admin.ch"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")

        response = self.app.post(
            f"{self.route_prefix}/generate",
            data=json.dumps({"url": "https://test.bgdi.ch/test"}),
            content_type="application/json",
            headers={"Origin": "map.geo.admin.ch"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], "map.geo.admin.ch")
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], "GET, POST, OPTIONS")

        response = self.app.post(
            f"{self.route_prefix}/generate",
            data=json.dumps({"url": "https://example.swisstopo.cloud/test"}),
            content_type="application/json",
            headers={"Origin": "map.geo.admin.ch"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], "map.geo.admin.ch")
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], "GET, POST, OPTIONS")

        response = self.app.post(
            f"{self.route_prefix}/generate",
            data=json.dumps({"url": "https://www.example.com/test"}),
            content_type="application/json",
            headers={"Origin": "map.geo.admin.ch"}
        )
        self.assertEqual(response.status_code, 400, msg="Domain restriction not applied")
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], "map.geo.admin.ch")
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], "GET, POST, OPTIONS")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json, {
                "error": {
                    "code": 400, "message": "URL domain not allowed"
                }, "success": False
            }
        )

        response = self.app.post(
            f"{self.route_prefix}/generate",
            data=json.dumps({"url": "https://www.example.com/test"}),
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
