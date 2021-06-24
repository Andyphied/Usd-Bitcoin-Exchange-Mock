from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware

from api.api import router
from core.config import settings
from core.middleware import RequestContextLogMiddleware
from core.logger import setup_logging


def create_app():
    app = FastAPI(title=settings.API_TITLE)

    app.include_router(router)

    app.add_middleware(CORSMiddleware,
                       allow_origins=['*'],
                       allow_credentials=True,
                       allow_methods=['*'],
                       allow_headers=['*'])

    app.add_middleware(RequestContextLogMiddleware)
    setup_logging()

    return app
