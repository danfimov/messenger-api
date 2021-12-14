from aiohttp.web import json_response
from aiohttp_pydantic.oas.typing import r200
from aiohttp_pydantic import PydanticView
from messenger.api.v1.models import AppOnlineResponse


class PingView(PydanticView):
    URL_PATH = '/ping'

    async def get(self) -> r200[AppOnlineResponse]:
        """
        Pings the application to see if it has started.

        Tags: Ping application
        Status Codes:
            200: App is online
            500: App is down
        """
        return json_response(AppOnlineResponse().dict())
