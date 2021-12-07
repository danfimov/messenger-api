from http import HTTPStatus
from pydantic import ValidationError
from aiohttp.web import json_response, Response

from .base import BaseView, db_required
from ..errors import ChatNotFound, UserNotFound, BadParametersError

from ..models import ChatCreateMessageRequest, ChatCreateMessageResponse, \
    Message, ChatGetMessagesResponse, \
    ChatGetMessagesRequest


class MessagesView(BaseView):
    URL_PATH = '/v1/chats/{chat_id}/messages'

    @db_required()
    async def post(self) -> Response:
        body = await self.request.json()
        params = self.request.rel_url.query
        try:
            parsed_request = ChatCreateMessageRequest(
                user_id=params['user_id'],
                chat_id=self.request.match_info['chat_id'],
                **body
            )
        except ValidationError:
            return BadParametersError()

        if await self.db_manager.is_chat_id_exist(parsed_request.chat_id):
            if await self.db_manager.is_rel_id_in_chat(parsed_request.chat_id,
                                                       parsed_request.user_id):
                message_id = await self.db_manager.create_message(
                    parsed_request.message,
                    parsed_request.chat_id,
                    parsed_request.user_id
                )
                return json_response(
                    ChatCreateMessageResponse(message_id=message_id).dict(),
                    status=HTTPStatus.CREATED
                )
            else:
                return UserNotFound()
        else:
            return ChatNotFound()

    @db_required()
    async def get(self) -> Response:
        params = self.request.rel_url.query
        iterator = params.get('from')
        try:
            parsed_request = ChatGetMessagesRequest(
                chat_id=self.request.match_info['chat_id'],
                from_=iterator,
                **params
            )
        except ValidationError:
            return BadParametersError()

        if await self.db_manager.is_chat_id_exist(
                parsed_request.chat_id):

            messages = await self.db_manager.get_messages(
                parsed_request.chat_id,
                parsed_request.limit,
                parsed_request.from_)

            if messages is not None:
                messages = [
                    Message(text=text) for text in messages
                ]
                iterator = int(parsed_request.from_) if parsed_request.from_ else 0
                iterator = {"iterator": str(len(messages) + iterator)}
            else:
                messages = []
                iterator = None

            response_obj = ChatGetMessagesResponse.parse_obj(
                {'messages': messages, 'next': iterator})
            return json_response(response_obj.dict(exclude_none=True),
                                 status=HTTPStatus.OK)
        else:
            return ChatNotFound()
