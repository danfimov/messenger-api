from aiohttp.web import json_response, Response

from .base import BaseView, db_required
from ..models import QuitResponse


class QuitView(BaseView):
    URL_PATH = '/v1/quit'

    @db_required()
    async def post(self) -> Response:
        session_id = self.request.headers.get('session_id')
        await self.db_manager.delete_session(session_id)
        return json_response(QuitResponse().dict())
