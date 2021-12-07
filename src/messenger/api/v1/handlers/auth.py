from http import HTTPStatus
from aiohttp.web import json_response, Response

from .base import BaseView, db_required
from ..models import AuthUserRequest, AuthUserResponse
from ..errors import InvalidLoginPassword


class AuthenticationView(BaseView):
    URL_PATH = '/v1/auth'

    @db_required()
    async def get(self) -> Response:
        body = await self.request.json()
        user = AuthUserRequest.parse_obj(body)
        user_id = await self.db_manager.authentication(
            user_name=user.user_name,
            password=user.password
        )
        if user_id:
            session_id = await self.db_manager.create_session(user_id)
            return json_response(AuthUserResponse(session_id=session_id).dict(), status=HTTPStatus.OK)
        return InvalidLoginPassword()
