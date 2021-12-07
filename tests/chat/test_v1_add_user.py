from http import HTTPStatus
from tests.conftest import CREATE_CHAT_URL, ADD_USER_URL


async def test_v1_add_user(api_client, auth_default_user):
    session_id = auth_default_user
    headers = {'session_id': session_id}

    data = {'chat_name': 'new chat!'}
    response = await api_client.post(CREATE_CHAT_URL, json=data, headers=headers)
    assert response.status == HTTPStatus.CREATED

    body = await response.json()
    chat_id = body.get('chat_id', None)

    data = {"user_name": "Vasya Pupkin"}
    response = await api_client.post(ADD_USER_URL.format(chat_id), json=data, headers=headers)
    assert response.status == HTTPStatus.CREATED

    body = await response.json()
    assert body.get('user_id') is not None


async def test_v1_add_user_twice(api_client, auth_default_user):
    session_id = auth_default_user
    headers = {'session_id': session_id}

    data = {'chat_name': 'new chat!'}
    response = await api_client.post(CREATE_CHAT_URL, json=data, headers=headers)
    assert response.status == HTTPStatus.CREATED

    body = await response.json()
    chat_id = body.get('chat_id', None)

    data = {"user_name": "Vasya Pupkin"}
    response = await api_client.post(ADD_USER_URL.format(chat_id), json=data, headers=headers)
    assert response.status == HTTPStatus.CREATED

    response = await api_client.post(ADD_USER_URL.format(chat_id), json=data, headers=headers)
    assert response.status == HTTPStatus.BAD_REQUEST


async def test_v1_add_user_in_non_exist_chat(api_client, auth_default_user):
    session_id = auth_default_user
    headers = {'session_id': session_id}

    chat_id = 'bad-chat_id'
    data = {"user_name": "Vasya Pupkin"}
    response = await api_client.post(ADD_USER_URL.format(chat_id), json=data, headers=headers)
    assert response.status == HTTPStatus.NOT_FOUND
