import logging
import re
import time

from werkzeug.exceptions import HTTPException

from flask import Flask
from flask import abort
from flask import g
from flask import request

from app import settings
from app.helpers.utils import ALLOWED_DOMAINS_PATTERN
from app.helpers.utils import make_error_msg

logger = logging.getLogger(__name__)
route_logger = logging.getLogger('app.routes')

# Standard Flask application initialisation

app = Flask(__name__)
app.config.from_object(settings)


# NOTE it is better to have this method registered first (before validate_origin) otherwise
# the route might not be logged if another method reject the request.
@app.before_request
def log_route():
    g.setdefault('request_started', time.time())
    route_logger.info('%s %s', request.method, request.path)


# Reject request from non allowed origins
@app.before_request
def validate_origin():
    if 'Origin' not in request.headers:
        logger.error('Origin header is not set')
        abort(403, 'Not allowed')
    if not re.match(ALLOWED_DOMAINS_PATTERN, request.headers['Origin']):
        logger.error('Origin=%s is not allowed', request.headers['Origin'])
        abort(403, 'Not allowed')


# Add CORS Headers to all request
@app.after_request
def add_cors_header(response):
    if (
        'Origin' in request.headers and
        re.match(ALLOWED_DOMAINS_PATTERN, request.headers['Origin'])
    ):
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


# NOTE it is better to have this method registered last (after add_cors_header) otherwise
# the response might not be correct (e.g. headers added in another after_request hook).
@app.after_request
def log_response(response):
    route_logger.info(
        "%s %s - %s",
        request.method,
        request.path,
        response.status,
        extra={
            'response':
                {
                    "status_code": response.status_code, "headers": dict(response.headers.items())
                },
            "duration": time.time() - g.get('request_started', time.time())
        }
    )
    return response


# Register error handler to make sure that every error returns a json answer
@app.errorhandler(Exception)
def handle_exception(err):
    """Return JSON instead of HTML for HTTP errors."""
    if isinstance(err, HTTPException):
        logger.error(err)
        return make_error_msg(err.code, err.description)

    logger.exception('Unexpected exception: %s', err)
    return make_error_msg(500, "Internal server error, please consult logs")


from app import routes  # isort:skip pylint: disable=wrong-import-position
