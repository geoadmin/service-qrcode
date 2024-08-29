import logging
import re
import time

from werkzeug.exceptions import HTTPException

from flask import Flask
from flask import g
from flask import request

from app import settings
from app.helpers.utils import make_error_msg
from app.settings import ALLOWED_DOMAINS_PATTERN
from app.settings import CACHE_CONTROL
from app.settings import CACHE_CONTROL_4XX

logger = logging.getLogger(__name__)
route_logger = logging.getLogger('app.routes')

# Standard Flask application initialisation

app = Flask(__name__)
app.config.from_object(settings)


def is_domain_allowed(domain):
    return re.match(ALLOWED_DOMAINS_PATTERN, domain) is not None


# NOTE it is better to have this method registered first (before validate_origin) otherwise
# the route might not be logged if another method reject the request.
@app.before_request
def log_route():
    g.setdefault('request_started', time.time())
    route_logger.info('%s %s', request.method, request.path)


# Add CORS Headers to all request
@app.after_request
def add_cors_header(response):
    # Only add CORS header if an origin or referer header is present in request
    # is a host part of our whitelist
    cors_origin = None
    if 'Origin' in request.headers and is_domain_allowed(request.headers['Origin']):
        cors_origin = request.headers['Origin']

    if 'Referer' in request.headers and is_domain_allowed(request.headers['Referer']):
        cors_origin = request.headers['Referer']

    if cors_origin:
        response.headers['Access-Control-Allow-Origin'] = cors_origin
        response.headers['Vary'] = 'Origin'
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'

    return response


@app.after_request
def add_cache_control_header(response):
    # For /checker route we let the frontend proxy decide how to cache it.
    if request.method == 'GET' and request.endpoint != 'checker':
        if response.status_code >= 400:
            response.headers.set('Cache-Control', CACHE_CONTROL_4XX)
        else:
            response.headers.set('Cache-Control', CACHE_CONTROL)
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
