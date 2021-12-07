from http import HTTPStatus

from aiohttp.web import json_response

from .base import BaseView, db_required
from ..models import ChatCreateResponse, ChatCreateRequest


class CreateChatView(BaseView):
    URL_PATH = '/v1/chats'

    @db_required()
    async def post(self):
        body = await self.request.json()
        parsed_data = ChatCreateRequest.parse_obj(body)
        new_chat_id = await self.db_manager.create_chat(
            parsed_data.chat_name)
        return json_response(ChatCreateResponse(chat_id=str(new_chat_id)).dict(),
                             status=HTTPStatus.CREATED)
