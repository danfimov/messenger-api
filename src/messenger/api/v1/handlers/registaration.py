from http import HTTPStatus
from aiohttp.web import json_response, Response

from .base import BaseView, db_required
from ..models import CreateUserRequest, UserCreatedResponse
from ..errors import LoginAlreadyExists


class RegistrationView(BaseView):
    URL_PATH = '/v1/reg'

    @db_required()
    async def post(self) -> Response:
        body = await self.request.json()
        user = CreateUserRequest.parse_obj(body)
        if await self.db_manager.create_user(user):
            return json_response(
                UserCreatedResponse().dict(),
                status=HTTPStatus.CREATED
            )
        return LoginAlreadyExists()
