import os
import multiprocessing
from gunicorn.app.base import BaseApplication
from app import app as application


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    SERVICE_QR_CODE_HTTP_PORT = str(os.environ.get('SERVICE_QR_CODE_HTTP_PORT'))
    options = {
        'bind': '%s:%s' % ('0.0.0.0', SERVICE_QR_CODE_HTTP_PORT),
        'worker_class': 'gevent',
        'workers': number_of_workers(),
        'timeout': 60,
    }
    StandaloneApplication(application, options).run()
