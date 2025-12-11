# Initialize OTEL.
# Initialize should be called as early as possible, but at least before the app is imported
# The order has a impact on how the libraries are instrumented. If called after app import,
# e.g. the flask instrumentation has no effect. See:
# https://github.com/open-telemetry/opentelemetry.io/blob/main/content/en/docs/zero-code/python/troubleshooting.md#use-programmatic-auto-instrumentation

from opentelemetry.instrumentation.auto_instrumentation import initialize

initialize()

import os

from gunicorn.app.base import BaseApplication

from app.app import app as application
from app.helpers.utils import get_logging_cfg
from app.settings import GUNICORN_KEEPALIVE

from app.helpers.utils import strtobool
from app.helpers import otel

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

    # Setup OTEL providers for this worker
    if not strtobool(os.getenv("OTEL_SDK_DISABLED", "false")):
        otel.setup_trace_provider(worker.pid)

class StandaloneApplication(BaseApplication):  # pylint: disable=abstract-method

    def __init__(self, app, options=None):  # pylint: disable=redefined-outer-name
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value for key,
            value in self.options.items() if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

# We use the port 5000 as default, otherwise we set the HTTP_PORT env variable within the container.
if __name__ == '__main__':
    HTTP_PORT = str(os.environ.get('HTTP_PORT', "5000"))
    # Bind to 0.0.0.0 to let your app listen to all network interfaces.
    options = {
        'bind': f"0.0.0.0:{HTTP_PORT}",
        'worker_class': 'gevent',
        'workers': 2,  # scaling horizontally is left to Kubernetes
        'timeout': 60,
        'keepalive': GUNICORN_KEEPALIVE,
        'logconfig_dict': get_logging_cfg(),
        'post_fork': post_fork,
    }
    StandaloneApplication(application, options).run()
