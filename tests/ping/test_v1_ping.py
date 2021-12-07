from http import HTTPStatus
from tests.conftest import PING_URL


async def test_v1_ping(api_client):
    response = await api_client.get(PING_URL)
    assert response.status == HTTPStatus.OK
