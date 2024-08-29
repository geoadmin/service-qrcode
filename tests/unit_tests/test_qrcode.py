import io
import re
import unittest
from urllib.parse import quote

from nose2.tools import params
from PIL import Image
from pyzbar import pyzbar

from flask import url_for

from app.app import app
from app.settings import ALLOWED_DOMAINS_PATTERN
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

    def assertCors(self, response):  # pylint: disable=invalid-name
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIsNotNone(
            re.match(ALLOWED_DOMAINS_PATTERN, response.headers['Access-Control-Allow-Origin']),
            msg=f"Access-Control-Allow-Origin={response.headers['Access-Control-Allow-Origin']}"
            f" doesn't match {ALLOWED_DOMAINS_PATTERN}"
        )
        self.assertIn('Access-Control-Allow-Methods', response.headers)
        self.assertListEqual(
            sorted(['GET', 'HEAD', 'OPTIONS']),
            sorted(
                map(
                    lambda m: m.strip(),
                    response.headers['Access-Control-Allow-Methods'].split(',')
                )
            )
        )
        self.assertIn('Access-Control-Allow-Headers', response.headers)
        self.assertEqual(response.headers['Access-Control-Allow-Headers'], '*')

    def assertNoCors(self, response):  # pylint: disable=invalid-name
        self.assertNotIn('Access-Control-Allow-Origin', response.headers)
        self.assertNotIn('Access-Control-Allow-Methods', response.headers)
        self.assertNotIn('Access-Control-Allow-Headers', response.headers)

    def test_checker(self):
        response = self.app.get(url_for('checker'), headers=self.valid_origin_header)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Cache-Control', response.headers)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json, {"message": "OK", "success": True, "version": APP_VERSION})

    def test_generate_errors(self):
        response = self.app.post(url_for('generate_get'), headers=self.valid_origin_header)
        self.assertEqual(response.status_code, 405, msg="POST method is not allowed")
        self.assertCors(response)
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
        self.assertCors(response)
        self.assertIn('Cache-Control', response.headers, msg="Cache control header missing")
        self.assertIn(
            'max-age=', response.headers['Cache-Control'], msg="Cache Control max-age not set"
        )
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json, {
                "error": {
                    "code": 400, "message": "Missing parameter 'url'"
                }, "success": False
            }
        )

    def test_no_origin_allowed(self):
        response = self.app.get(
            url_for('generate_get'),
            query_string={'url': 'https://some_random_domain/test'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNoCors(response)

    def test_referer_check(self):
        response = self.app.get(
            url_for('generate_get'),
            query_string={'url': 'https://some_random_domain/test'},
            headers={'Referer': 'some_random_domain'}
        )
        self.assertEqual(
            response.status_code, 200, msg="Allowed Referer did not returned an HTTP 200"
        )
        self.assertCors(response)

    def test_generate_url_domain_restriction(self):
        response = self.app.get(
            url_for('generate_get'),
            query_string={'url': 'https://www.example.com/test'},
            headers=self.valid_origin_header
        )
        self.assertEqual(response.status_code, 400, msg="Domain restriction not applied")
        self.assertCors(response)
        self.assertIn('Cache-Control', response.headers, msg="Cache control header missing")
        self.assertIn(
            'max-age=3600', response.headers['Cache-Control'], msg="Cache Control max-age not set"
        )
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json, {
                "error": {
                    "code": 400, "message": "URL domain not allowed"
                }, "success": False
            }
        )

    @params(
        None,
        {'Origin': 'www.example'},
        {
            'Origin': 'www.example', 'Sec-Fetch-Site': 'cross-site'
        },
        {
            'Origin': 'www.example', 'Sec-Fetch-Site': 'same-site'
        },
        {
            'Origin': 'www.example', 'Sec-Fetch-Site': 'same-origin'
        },
        {'Referer': 'http://www.example'},
    )
    def test_generate_origin_not_allowed(self, headers):
        response = self.app.get(
            url_for('generate_get'),
            query_string={'url': 'https://some_random_domain/test'},
            headers=headers
        )
        self.assertNoCors(response)
        self.assertIn('Cache-Control', response.headers, msg="Cache control header missing")
        self.assertIn(
            'max-age=', response.headers['Cache-Control'], msg="Cache Control max-age not set"
        )
        self.assertEqual(response.status_code, 200)

    @params(
        {'Origin': 'map.geo.admin.ch'},
        {
            'Origin': 'map.geo.admin.ch', 'Sec-Fetch-Site': 'same-site'
        },
        {
            'Origin': 'public.geo.admin.ch', 'Sec-Fetch-Site': 'same-origin'
        },
        {
            'Origin': 'http://localhost', 'Sec-Fetch-Site': 'cross-site'
        },
        {'Referer': 'https://map.geo.admin.ch'},
    )
    def test_generate_origin_allowed(self, headers):
        response = self.app.get(
            url_for('generate_get'),
            query_string={'url': 'https://some_random_domain/test'},
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertCors(response)
        self.assertEqual(response.content_type, "image/png")
        self.assertIn('Cache-Control', response.headers, msg="Cache control header missing")
        self.assertIn(
            'max-age=', response.headers['Cache-Control'], msg="Cache Control max-age not set"
        )

    def test_generate(self):
        long_string_quoted = "value with space & special character !?"
        url_orig = f'https://some_random_domain/test?arg1=value2&arg2={quote(long_string_quoted)}'
        response = self.app.get(
            url_for('generate_get'),
            query_string={'url': url_orig},
            headers=self.valid_origin_header
        )
        self.assertEqual(response.status_code, 200)
        self.assertCors(response)
        self.assertEqual(response.content_type, "image/png")
        self.assertIn('Cache-Control', response.headers, msg="Cache control header missing")
        self.assertIn(
            'max-age=', response.headers['Cache-Control'], msg="Cache Control max-age not set"
        )

        # decode the qrcode image into the url
        image = io.BytesIO(response.data)
        data = pyzbar.decode(Image.open(image))
        url_decoded = data[0].data.decode('utf-8')
        self.assertEqual(url_orig, url_decoded, msg="Decoded url from image not equal to original")
