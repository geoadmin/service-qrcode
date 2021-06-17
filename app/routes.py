import logging
from io import BytesIO

import qrcode

from flask import abort
from flask import jsonify
from flask import make_response
from flask import request

from app import app
from app.helpers import make_error_msg
from app.helpers.route import prefix_route
from app.helpers.url import validate_url
from app.version import APP_VERSION

logger = logging.getLogger(__name__)

# add route prefix
app.route = prefix_route(app.route, '/v4/qrcode')


@app.route('/checker', methods=['GET'])
def check():
    return make_response(jsonify({'success': True, 'message': 'OK', 'version': APP_VERSION}))


@app.route('/generate', methods=['POST'])
def generate():
    content = request.json
    # sanity check
    if content is None or 'url' not in content:
        logger.error("The property 'url' is missing from the request body")
        abort(make_error_msg(400, "The property 'url' is missing from the request body"))
    if not isinstance(content['url'], str):
        logger.error("Invalid property 'url' in request body, must be a string")
        abort(make_error_msg(400, "Invalid property 'url' in request body, must be a string"))

    url = validate_url(content['url'])

    logger.debug('generate request with url=%s', url)

    # For a qrcode of 128px
    qr_code = qrcode.QRCode(box_size=4, error_correction=qrcode.constants.ERROR_CORRECT_L, border=3)
    qr_code.add_data(url)
    qr_code.make()
    output = BytesIO()
    img = qr_code.make_image()
    img.save(output)

    response = make_response(output.getvalue())
    response.headers.set('Content-Type', 'image/png')
    return response
