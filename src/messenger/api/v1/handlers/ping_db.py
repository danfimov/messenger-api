from http import HTTPStatus
from aiohttp.web import json_response, Response
from messenger.api.v1.handlers.base import BaseView
from messenger.api.v1.models import DatabaseOnlineResponse, \
    DatabaseOfflineResponse


class PingDbView(BaseView):
    URL_PATH = '/ping_db'

    async def get(self) -> Response:
        if await self.db_manager.ping_db():
            return json_response(DatabaseOnlineResponse().dict(),
                                 status=HTTPStatus.OK)
        else:
            return json_response(DatabaseOfflineResponse().dict(),
                                 status=HTTPStatus.SERVICE_UNAVAILABLE)
