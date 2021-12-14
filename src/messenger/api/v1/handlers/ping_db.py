from http import HTTPStatus
from aiohttp.web import json_response
from aiohttp_pydantic.oas.typing import r200, r503
from typing import Union
from aiohttp_pydantic import PydanticView
from messenger.api.v1.models import DatabaseOnlineResponse, \
    DatabaseOfflineResponse
from messenger.api.v1.handlers.base import BaseView


class PingDbView(PydanticView, BaseView):
    URL_PATH = '/ping_db'

    async def get(self) -> \
            Union[r200[DatabaseOnlineResponse], r503[DatabaseOfflineResponse]]:
        """
        Pings the application's database with simple query.

        Tags: Ping application
        Status Codes:
            200: Database is up
            503: Database is down
        """
        if await self.request.app['db_manager'].ping_db():
            return json_response(DatabaseOnlineResponse().dict())
        else:
            return json_response(DatabaseOfflineResponse().dict(),
                                 status=HTTPStatus.SERVICE_UNAVAILABLE)
