from messenger.api.v1.handlers.ping_db import PingDbView
from messenger.api.v1.handlers.ping import PingView
from messenger.api.v1.handlers.create_chat import CreateChatView
from messenger.api.v1.handlers.registaration import RegistrationView
from messenger.api.v1.handlers.add_user_to_chat import AddUserToChatView
from messenger.api.v1.handlers.messages import MessagesView
from messenger.api.v1.handlers.auth import AuthenticationView
from messenger.api.v1.handlers.quit import QuitView
from messenger.api.v1.handlers.search import SearchBeginView, \
    SearchTaskStatusView, SearchResultView

HANDLERS = (
    PingDbView,
    PingView,
    RegistrationView,
    AuthenticationView,
    QuitView,
    CreateChatView,
    AddUserToChatView,
    MessagesView,
    SearchBeginView,
    SearchTaskStatusView,
    SearchResultView,
)
