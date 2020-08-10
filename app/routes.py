from io import BytesIO
from urllib.parse import quote

import qrcode

from flask import abort
from flask import current_app as capp
from flask import jsonify
from flask import make_response
from flask import request

from app import app
from app.helpers import make_error_msg
from app.helpers.route import prefix_route
from app.helpers.route import check_version
from app.helpers.url import validate_url

# add route prefix
app.route = prefix_route(app.route, '/v<int:version>/qrcode')


@app.route('/checker', methods=['GET'])
@check_version(min_version=4)
def check(version):
    return make_response(jsonify({'success': True, 'message': 'OK'}))


@app.route('/generate', methods=['POST'])
@check_version(min_version=4)
def generate(version):
    content = request.json
    # sanity check
    if content is None or 'url' not in content:
        capp.logger.error("The property 'url' is missing from the request body")
        abort(make_error_msg(400, "The property 'url' is missing from the request body"))
    if not isinstance(content['url'], str):
        capp.logger.error("Invalid property 'url' in request body, must be a string")
        abort(make_error_msg(400, "Invalid property 'url' in request body, must be a string"))

    url = quote(validate_url(content['url']))

    capp.logger.debug('generate request with url=%s', url)

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
