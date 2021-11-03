import unittest
from urllib.parse import quote
import io

from flask import url_for
from PIL import Image
from pyzbar import pyzbar

from app import app
from app.version import APP_VERSION


class QrCodeTests(unittest.TestCase):

    def setUp(self):
        self.context = app.test_request_context()
        self.context.push()
        self.app = app.test_client()
        self.assertEqual(app.debug, False)
        self.valid_origin_header = {
            # see .env.test
            'Origin': 'some_random_domain'
        }

    def test_checker(self):
        response = self.app.get(url_for('check'), headers=self.valid_origin_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json, {"message": "OK", "success": True, "version": APP_VERSION})

    def test_generate_errors(self):
        response = self.app.get(url_for('generate_get'))
        self.assertEqual(response.status_code, 403, msg="ORIGIN must be set")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json, {
                "error": {
                    "code": 403, "message": "Not allowed"
                }, "success": False
            }
        )
        response = self.app.post(url_for('generate_get'), headers=self.valid_origin_header)
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

        response = self.app.get(url_for('generate_get'), headers=self.valid_origin_header)
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
            url_for('generate_get'),
            query_string={'url': 'https://some_random_domain/test'},
            headers=self.valid_origin_header
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], "some_random_domain")
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], "GET, POST, OPTIONS")

        response = self.app.get(
            url_for('generate_get'),
            query_string={'url': 'https://www.example.com/test'},
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
            url_for('generate_get'),
            query_string={'url': 'https://www.example.com/test'},
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

    def test_generate(self):
        url_orig = f'https://some_random_domain/test?arg1=value2&arg2={quote("value with space & special character !?")}'
        response = self.app.get(
            url_for('generate_get'),
            query_string={'url': url_orig},
            headers=self.valid_origin_header
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], "some_random_domain")
        self.assertEqual(response.headers['Access-Control-Allow-Methods'], "GET, POST, OPTIONS")

        # decode the qrcode image into the url
        image = io.BytesIO(response.data)
        data = pyzbar.decode(Image.open(image))
        url_decoded = data[0].data.decode('utf-8')
        self.assertEqual(url_orig, url_decoded, msg="Decoded url from image not equal to original")