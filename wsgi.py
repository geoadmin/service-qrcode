import os
import multiprocessing
from gunicorn.app.base import BaseApplication
from app import app as application


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
    HTTP_PORT = str(os.environ.get('HTTP_PORT'), "8080")
    options = {
        'bind': '%s:%s' % ('0.0.0.0', HTTP_PORT),
        'worker_class': 'gevent',
        'workers': 2,
        'timeout': 60,
    }
    StandaloneApplication(application, options).run()
