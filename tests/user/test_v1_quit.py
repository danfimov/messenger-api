from http import HTTPStatus
from tests.conftest import QUIT_URL


async def test_v1_quit_once(api_client, auth_default_user):
    session_id = auth_default_user
    response = await api_client.post(QUIT_URL, headers={'session_id': session_id})

    assert response.status == HTTPStatus.OK


async def test_v1_quit_twice(api_client, auth_default_user):
    session_id = auth_default_user
    response = await api_client.post(QUIT_URL, headers={'session_id': session_id})
    assert response.status == HTTPStatus.OK

    response = await api_client.post(QUIT_URL, headers={'session_id': session_id})
    assert response.status == HTTPStatus.NOT_FOUND
