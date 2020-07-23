import unittest
import json

from app import app


class QrCodeTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.assertEqual(app.debug, False)
        self.route_prefix = '/v4/qrcode'

    def tearDown(self):
        pass

    def test_checker(self):
        response = self.app.get(f'{self.route_prefix}/checker')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertEqual(response.data.decode('utf-8'), "OK")

    def test_generate(self):
        response = self.app.get(f'{self.route_prefix}/generate')
        self.assertEqual(response.status_code, 405, msg="GET method is not allowed")

        response = self.app.post(f'{self.route_prefix}/generate')
        self.assertEqual(response.status_code, 400, msg="JSON body is requested")

        response = self.app.post(
            f'{self.route_prefix}/generate',
            data=json.dumps({'url': "https://example.com"}),
            content_type='text/html'
        )
        self.assertEqual(response.status_code, 400, msg="Only JSON body is accepted")

    def test_generate_domain_restriction(self):

        response = self.app.post(
            f'{self.route_prefix}/generate',
            data=json.dumps({'url': "https://map.geo.admin.ch/test"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")

        response = self.app.post(
            f'{self.route_prefix}/generate',
            data=json.dumps({'url': "https://test.bgdi.ch/test"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")

        response = self.app.post(
            f'{self.route_prefix}/generate',
            data=json.dumps({'url': "https://example.swisstopo.cloud/test"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")

        response = self.app.post(
            f'{self.route_prefix}/generate',
            data=json.dumps({'url': "https://www.example.com/test"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.status_code, 400, msg="Domain restriction not applied")
