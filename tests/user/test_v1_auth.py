from http import HTTPStatus
from tests.conftest import DEFAULT_USER, AUTH_URL


async def test_v1_auth_ok(api_client, reg_default_user):
    data = DEFAULT_USER

    response = await api_client.get(AUTH_URL, json=data)
    assert response.status == HTTPStatus.OK


async def test_v1_auth_wrong_login(api_client):
    data = {'user_name': 'Wrong-login',
            'password': 'password'}

    response = await api_client.get(AUTH_URL, json=data)
    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_v1_auth_wrong_password(api_client):
    data = DEFAULT_USER
    data['password'] = 'wrong_password'

    response = await api_client.get(AUTH_URL, json=data)
    assert response.status == HTTPStatus.UNAUTHORIZED
