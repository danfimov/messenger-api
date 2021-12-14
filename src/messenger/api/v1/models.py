from typing import Optional
from pydantic import Field, BaseModel, StrictStr
from enum import IntEnum
from typing import ClassVar
from http import HTTPStatus


class DefaultResponse(BaseModel):
    status: ClassVar[int] = Field(default=HTTPStatus.OK)


class DefaultErrorResponse(BaseModel):
    message: str = Field(description='error reason')
    info: Optional[str] = Field(description='addition information')
    status: ClassVar[int] = Field(default=HTTPStatus.BAD_REQUEST)


class InvalidLoginPassword(DefaultErrorResponse):
    message = 'wrong-login-or-password'
    status = HTTPStatus.UNAUTHORIZED


class ChatJoinRequest(BaseModel):
    chat_id: str
    user_id: str
    user_name: str = Field(max_length=255)


class ChatJoinResponse(BaseModel):
    user_id: str = Field(description='id of the user added to the chat')


class ChatCreateRequest(BaseModel):
    chat_name: str = Field(alias='chat_name', max_length=255)


class ChatCreateResponse(BaseModel):
    chat_id: str = Field(description='id of the created chat')


class ChatCreateMessageRequest(BaseModel):
    user_id: str
    chat_id: str
    message: str = Field(alias='message')


class ChatCreateMessageResponse(BaseModel):
    message_id: str = Field(default='string')


class Message(BaseModel):
    text: StrictStr


class ChatGetMessagesRequest(BaseModel):
    limit: int = Field(gt=0, lt=1000)
    from_: Optional[int] = Field(alias='from', gt=-1)
    chat_id: str


class ChatGetMessagesResponse(BaseModel):
    messages: list[Message]
    next: Optional[dict] = Field(alias='next')


class AppOnlineResponse(BaseModel):
    message: str = "app-is-online"


class DatabaseOnlineResponse(BaseModel):
    message: str = 'database-is-up'


class DatabaseOfflineResponse(BaseModel):
    message: str = 'database-is-down'


class CreateUserRequest(BaseModel):
    user_name: str = Field(max_length=255)
    password: str = Field(max_length=255)


class UserCreatedResponse(BaseModel):
    message: str = 'user-created'


class AuthUserRequest(BaseModel):
    user_name: str = Field(max_length=255)
    password: str = Field(max_length=255)


class AuthUserResponse(BaseModel):
    session_id: str = Field(description='unique session id')


class QuitResponse(BaseModel):
    message: str = 'successful-quit'


class SearchBeginRequest(BaseModel):
    message: str


class SearchBeginResponse(BaseModel):
    task_id: str


class SearchTaskStatusRequest(BaseModel):
    task_id: str


class TaskStatus(IntEnum):
    waiting = 0
    in_progress = 1
    done = 2
    failed = 3


class SearchTaskStatusResponse(BaseModel):
    status: str


class SearchResultRequest(BaseModel):
    limit: int = Field(gt=0, lt=1000)
    from_: Optional[int] = Field(alias='from', gt=-1)
    task_id: str


class SearchResultResponse(BaseModel):
    messages: list
    next: Optional[dict] = Field(alias='next')
