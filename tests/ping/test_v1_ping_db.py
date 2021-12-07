from http import HTTPStatus
from unittest.mock import patch
from tests.conftest import PING_DB_URL, REG_URL


async def test_v1_ping_db_ok(api_client):
    response = await api_client.get(PING_DB_URL)
    assert response.status == HTTPStatus.OK


async def test_v1_ping_db_unavailable(api_client):
    with patch('messenger.db_postgres.manager.DataBaseManager.ping_db', return_value=False):
        response = await api_client.get(PING_DB_URL)
        assert response.status == HTTPStatus.SERVICE_UNAVAILABLE

        response = await api_client.post(REG_URL)
        assert response.status == HTTPStatus.BAD_REQUEST
