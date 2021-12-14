from aiohttp.web import json_response
from aiohttp_pydantic.oas.typing import r200, r401
from typing import Union
from aiohttp_pydantic import PydanticView

from .base import BaseView
from messenger.api.v1.models import AuthUserRequest, AuthUserResponse, \
    InvalidLoginPassword


class AuthenticationView(PydanticView, BaseView):
    URL_PATH = '/v1/auth'

    async def get(self, user: AuthUserRequest) -> Union[
            r200[AuthUserResponse], r401[InvalidLoginPassword]]:
        """
        User authentication in the application.
        Login data is exchanged for a session id.

        Tags: User
        Status Codes:
            200: User authenticated
            401: Wrong pair login-password
        """
        user_id = await self.db_manager.authentication(
            user_name=user.user_name,
            password=user.password
        )
        if user_id:
            session_id = await self.db_manager.create_session(user_id)
            return json_response(
                AuthUserResponse(session_id=session_id).dict())
        return json_response(
            InvalidLoginPassword().dict(),
            status=InvalidLoginPassword.status
        )
