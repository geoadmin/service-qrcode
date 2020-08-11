import json
import logging
import logging.config
from datetime import datetime

from flask import has_request_context
from flask import request


class JsonFormatter(logging.Formatter):

    def format(self, record):
        msg_obj = {
            'time': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelno,
            'levelname': record.levelname,
            'application': 'service-qrcode',
            'name': record.name,
            'message': record.msg % record.args,
            'request': None
        }
        if has_request_context():
            msg_obj.update({'request': {'url': request.url, 'data': request.get_json()}})
        return json.dumps(msg_obj)


def init_logging():
    logging.config.dictConfig(
        config={
            'version': 1,
            'disable_existing_loggers': False,
            'root': {
                'level': 'DEBUG', 'propagate': True, 'handlers': ['console']
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler', 'level': 'DEBUG'
                }
            },
            'loggers': {
                'nose2': {
                    'level': 'INFO'
                }
            }
        }
    )

    # Uses the default handler for all libraries (e.g. werkzeug)
    root = logging.getLogger()
    root.handlers[0].setFormatter(JsonFormatter())
