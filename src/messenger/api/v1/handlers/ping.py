from http import HTTPStatus
from aiohttp.web import json_response, Response
from messenger.api.v1.handlers.base import BaseView
from messenger.api.v1.models import AppOnlineResponse


class PingView(BaseView):
    URL_PATH = '/ping'

    @staticmethod
    async def get() -> Response:
        return json_response(AppOnlineResponse().dict(), status=HTTPStatus.OK)
