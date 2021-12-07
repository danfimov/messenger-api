from os import getenv
from uuid import uuid4
from yarl import URL
from sqlalchemy_utils import create_database, drop_database
import pytest
from types import SimpleNamespace
from messenger.db_postgres.make_config import make_alembic_config
from alembic.config import Config
from alembic.command import upgrade
from messenger.api.app import create_app
from messenger.api.v1.handlers.registaration import RegistrationView
from messenger.api.v1.handlers.auth import AuthenticationView
from messenger.api.v1.models import AuthUserResponse

from os import environ

PG_URL = getenv('TEST_PG_URL', 'postgresql://username:hackme@localhost/api')

DEFAULT_USER = {
    'user_name': 'John Doe',
    'password': 'password'
}

PING_DB_URL = '/ping_db'
PING_URL = '/ping'
REG_URL = 'v1/reg'
AUTH_URL = 'v1/auth'
CREATE_CHAT_URL = 'v1/chats'
ADD_USER_URL = 'v1/chats/{}/users'
MESSAGES_URL = '/v1/chats/{}/messages'
QUIT_URL = 'v1/quit'


@pytest.fixture
def postgres() -> str:
    """
    Создает временную БД для запуска теста.
    """
    tmp_name = '.'.join([uuid4().hex, 'pytest'])
    environ['POSTGRES_DB'] = tmp_name
    tmp_url = str(URL(PG_URL).with_path(tmp_name))
    create_database(tmp_url)

    try:
        yield tmp_url
    finally:
        drop_database(tmp_url)


@pytest.fixture
def alembic_config(postgres):
    """
    Создает файл конфигурации для alembic
    """
    cmd_options = SimpleNamespace(config='alembic.ini', name='alembic', pg_url=postgres, raiseerr=False, x=None)
    return make_alembic_config(cmd_options)


@pytest.fixture
def migrated_postgres(alembic_config: Config):
    """
    Проводит миграцции
    """
    upgrade(alembic_config, "head")


@pytest.fixture
async def api_client(aiohttp_client, migrated_postgres):
    app = create_app()
    client = await aiohttp_client(app)
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture
async def reg_default_user(api_client):
    data = DEFAULT_USER
    await api_client.post(RegistrationView.URL_PATH, json=data)


@pytest.fixture
async def auth_default_user(api_client, reg_default_user):
    data = DEFAULT_USER
    response = await api_client.get(AuthenticationView.URL_PATH, json=data)
    body = await response.json()
    session_id = AuthUserResponse.parse_obj(body).session_id
    return session_id
