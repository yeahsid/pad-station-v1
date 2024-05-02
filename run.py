from app.main import app
from uvicorn.workers import UvicornWorker
from gunicorn.app.base import BaseApplication

class Application(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == "__main__":
    """
    This script runs the application using uvicorn server with gunicorn.
    It starts the server on the specified host and port.
    """
    options = {
        'bind': '%s:%s' % ('0.0.0.0', '8000'),
        'workers': 4,
    }
    Application(app, options).run()