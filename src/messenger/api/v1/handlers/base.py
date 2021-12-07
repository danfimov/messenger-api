from aiohttp.web import View, Request
from typing import Callable
from ....db_postgres.manager import DataBaseManager
from ....api.v1.errors import BadParametersError


def db_required():
    def decorator(handler: Callable):
        async def wrapper(*args, **kwargs):
            if await DataBaseManager.ping_db():
                return await handler(*args, **kwargs)
            else:
                return BadParametersError()

        return wrapper

    return decorator


class BaseView(View):
    def __init__(self, request: Request):
        super().__init__(request)
        self.db_manager = request.app['db_manager']
