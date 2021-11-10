import logging
from io import BytesIO

import qrcode

from flask import abort
from flask import jsonify
from flask import make_response
from flask import request

from app import app
from app.helpers.url import validate_url
from app.version import APP_VERSION

logger = logging.getLogger(__name__)


@app.route('/checker', methods=['GET'])
def check():
    return make_response(jsonify({'success': True, 'message': 'OK', 'version': APP_VERSION}))


@app.route('/generate', methods=['GET'])
def generate_get():
    if 'url' not in request.args:
        logger.error("Missing parameter 'url'")
        abort(400, "Missing parameter 'url'")
    url = validate_url(request.args.get('url'))

    logger.debug('generate qrcode with url=%s', url)

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
