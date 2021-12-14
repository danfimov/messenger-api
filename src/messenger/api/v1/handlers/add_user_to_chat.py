from http import HTTPStatus
from aiohttp.web import json_response, Response

from messenger.api.v1.handlers.base import BaseView, db_required
from messenger.api.v1.errors import ChatNotFound, UserAlreadyInChat
from messenger.api.v1.models import ChatJoinResponse, ChatJoinRequest


class AddUserToChatView(BaseView):
    URL_PATH = '/v1/chats/{chat_id}/users'

    @db_required()
    async def post(self) -> Response:
        body = await self.request.json()
        session_id = self.request.headers.get('session_id')
        user_id = await self.db_manager.get_user_id_from_session(session_id)
        parsed_request = ChatJoinRequest(
            chat_id=self.request.match_info['chat_id'],
            user_id=user_id,
            **body,
        )
        if not await self.db_manager.is_user_id_in_chat(
                parsed_request.chat_id, user_id):
            if await self.db_manager.is_chat_id_exist(parsed_request.chat_id):
                user_id = await self.db_manager.add_user_to_chat(
                    chat_id=parsed_request.chat_id,
                    user_name=parsed_request.user_name,
                    user_id=parsed_request.user_id
                )
                return json_response(
                    ChatJoinResponse(user_id=user_id).dict(),
                    status=HTTPStatus.CREATED
                )
            return ChatNotFound()
        return UserAlreadyInChat()
