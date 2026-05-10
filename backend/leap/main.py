"""Entrypoints for the LEAP Tournament Platform API.

- dev:   hot-reload uvicorn server for local development
- start: multi-worker gunicorn server for production
"""

import os
from pathlib import Path

from leap.api.main import app
from leap.config.settings import get_settings


def dev() -> None:
    """Run the app in development mode with hot-reload."""
    import uvicorn

    settings = get_settings()
    package_dir = Path(__file__).parent

    uvicorn.run(
        "leap.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        reload_dirs=[str(package_dir)],
        log_level=os.getenv("LOG_LEVEL", settings.LOG_LEVEL).lower(),
    )


def start() -> None:
    """Run the app in production mode with gunicorn + uvicorn workers."""
    import gunicorn.app.base

    settings = get_settings()

    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, application, options=None):
            self.options = options or {}
            self.application = application
            super().__init__()

        def load_config(self):  # type: ignore[override]
            for key, value in self.options.items():
                self.cfg.set(key, value)  # type: ignore

        def load(self):
            return self.application

    options = {
        "bind": f"{settings.API_HOST}:{os.getenv('PORT', str(settings.API_PORT))}",
        "workers": int(os.getenv("WORKERS", str(settings.API_WORKERS))),
        "worker_class": "uvicorn.workers.UvicornWorker",
        "loglevel": os.getenv("LOG_LEVEL", settings.LOG_LEVEL).lower(),
        "timeout": int(os.getenv("WORKER_TIMEOUT", str(settings.API_WORKER_TIMEOUT))),
    }
    StandaloneApplication(app, options).run()


if __name__ == "__main__":
    dev()
