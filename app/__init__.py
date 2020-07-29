import re

from flask import Flask, request, abort

from app.helpers import make_error_msg
from app.helpers.url import ALLOWED_DOMAINS_PATTERN
from app.middleware import ReverseProxy

# Standard Flask application initialisation

app = Flask(__name__)
app.wsgi_app = ReverseProxy(app.wsgi_app, script_name='/')


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


# Reject request from non allowed origins
@app.before_request
def validate_origin():
    if (
        'Origin' in request.headers and
        not re.match(ALLOWED_DOMAINS_PATTERN, request.headers['Origin'])
    ):
        abort(make_error_msg(403, 'Domain not allowed'))


from app import routes  # pylint: disable=wrong-import-position


def main():
    app.run()


if __name__ == '__main__':
    """
    Entrypoint for the application. At the moment, we do nothing specific, but there might be
    preparatory steps in the future
    """
    main()
