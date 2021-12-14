from http import HTTPStatus

from aiohttp.web import Response, json_response
from messenger.api.v1.models import DefaultErrorResponse


class ClientError:
    def __init__(self, status: int, error: str):
        self._status = status
        self._error = error

    def __call__(self, info: dict = None, *args, **kwargs) -> Response:
        return json_response(
            data=DefaultErrorResponse(
                message=self._error, info=info
            ).dict(exclude_none=True),
            status=self._status,
        )


BadParametersError = ClientError(
    HTTPStatus.BAD_REQUEST,
    'bad-parameters'
)
MethodNotAllowed = ClientError(
    HTTPStatus.METHOD_NOT_ALLOWED,
    'method-not-allowed'
)
ChatNotFound = ClientError(
    HTTPStatus.NOT_FOUND,
    'chat-not-found'
)
UserNotFound = ClientError(
    HTTPStatus.NOT_FOUND,
    'user-not-found'
)
LoginAlreadyExists = ClientError(
    HTTPStatus.CONFLICT,
    'login-already-exist'
)
AuthorizationRequired = ClientError(
    HTTPStatus.UNAUTHORIZED,
    'session-id-required'
)
UserAlreadyInChat = ClientError(
    HTTPStatus.BAD_REQUEST,
    'user-already-in-chat'
)
TaskNotFound = ClientError(
    HTTPStatus.NOT_FOUND,
    'task-not-found'
)
