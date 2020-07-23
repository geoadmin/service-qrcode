from urllib.parse import urlparse
import re

from flask import abort

ALLOWED_DOMAIN = [
    r'.*\.geo\.admin\.ch',
    r'.*bgdi\.ch',
    r'.*\.swisstopo\.cloud',
]


def validate_url(url):
    '''Simple URL validation

    If the URL can be parsed and have a valid hostname/domain then the URL is returned otherwise it
    raises a HTTPException(400). See :attr:`ALLOWED_DOMAIN` for valid domain.

    Args:
        url: URL string to validate

    Returns:
        The validated url string

    Raises:
        HTTPException(400) if the URL is not valid
    '''
    try:
        result = urlparse(url)
    except ValueError as err:
        abort(400, f'Invalid URL, {err}')

    if result.hostname is None:
        abort(400, 'Invalid URL, could not determine the hostname')

    domain_pattern = '({})'.format('|'.join(ALLOWED_DOMAIN))
    if not re.match(domain_pattern, result.hostname):
        abort(400, 'URL domain not allowed')

    return url
