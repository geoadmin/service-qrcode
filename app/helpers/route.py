from functools import wraps

from flask import abort

from app.helpers import make_error_msg


def prefix_route(route_decorator, prefix='', fmt='{prefix}{route}'):
    '''Defines a new route decorator with a prefix.

    Args:
        route_decorator: route decorator to enhanced
        prefix: prefix to add to the route
        fmt: string format to use for adding the prefix

    Returns:
        new decorator with prefixed route.
    '''

    @wraps(route_decorator)
    def newroute(route, *args, **kwargs):
        '''New function to prefix the route'''
        return route_decorator(fmt.format(prefix=prefix, route=route), *args, **kwargs)

    return newroute


def check_version(version=4):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):
            if 'version' not in kwargs:
                abort(make_error_msg(400, 'api version not specified'))
            if kwargs['version'] != version:
                abort(make_error_msg(400, 'api version v%s not supported' % (kwargs["version"])))
            return function(*args, **kwargs)

        return wrapper

    return decorator
