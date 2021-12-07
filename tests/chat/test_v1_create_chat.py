from http import HTTPStatus
from tests.conftest import CREATE_CHAT_URL


async def test_v1_create_chat_ok(api_client, auth_default_user):
    session_id = auth_default_user
    headers = {'session_id': session_id}

    data = {'chat_name': 'new chat!'}

    response = await api_client.post(CREATE_CHAT_URL, json=data, headers=headers)
    body = await response.json()

    assert response.status == HTTPStatus.CREATED
    assert body.get('chat_id', None) is not None


async def test_v1_create_two_chat_with_same_name(api_client, auth_default_user):
    session_id = auth_default_user
    headers = {'session_id': session_id}

    data = {'chat_name': 'new chat!'}

    response = await api_client.post(CREATE_CHAT_URL, json=data, headers=headers)
    body_1 = await response.json()

    assert response.status == HTTPStatus.CREATED
    assert body_1.get('chat_id', None) is not None

    response = await api_client.post(CREATE_CHAT_URL, json=data, headers=headers)
    body_2 = await response.json()

    assert response.status == HTTPStatus.CREATED
    assert body_2.get('chat_id', None) is not None

    assert body_1.get('chat_id') != body_2.get('chat_id')
