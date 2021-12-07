from http import HTTPStatus
import pytest
from tests.conftest import CREATE_CHAT_URL, ADD_USER_URL, MESSAGES_URL


@pytest.fixture
async def user_in_chat(api_client, auth_default_user):
    session_id = auth_default_user
    headers = {'session_id': session_id}

    data = {'chat_name': 'new chat!'}
    response = await api_client.post(CREATE_CHAT_URL, json=data, headers=headers)

    body = await response.json()
    chat_id = body.get('chat_id', None)

    data = {"user_name": "Vasya Pupkin"}
    response = await api_client.post(ADD_USER_URL.format(chat_id), json=data, headers=headers)

    body = await response.json()
    user_id = body.get('user_id', None)

    return chat_id, user_id, headers


async def test_v1_create_and_read_0(api_client, auth_default_user, user_in_chat):
    chat_id, user_id, headers = user_in_chat

    limit = 1
    response = await api_client.get(MESSAGES_URL.format(chat_id) + f'?limit={limit}', headers=headers)
    assert response.status == HTTPStatus.OK

    body = await response.json()
    messages = body.get('messages')
    assert messages is not None
    assert messages == []

    next_ = body.get('next')
    assert next_ is None


async def test_v1_create_and_read_1(api_client, auth_default_user, user_in_chat):
    chat_id, user_id, headers = user_in_chat

    data = {'message': 'Hello, world!'}

    response = await api_client.post(MESSAGES_URL.format(chat_id) + f'?user_id={user_id}', headers=headers, json=data)
    assert response.status == HTTPStatus.CREATED

    limit = 1
    response = await api_client.get(MESSAGES_URL.format(chat_id) + f'?limit={limit}', headers=headers)
    assert response.status == HTTPStatus.OK

    body = await response.json()
    messages = body.get('messages')
    assert messages is not None
    assert messages == [{'text': 'Hello, world!'}]

    next_ = body.get('next')
    assert next_ is not None
    assert next_ == {'iterator': '1'}


async def test_v1_create_bad_user_id(api_client, auth_default_user, user_in_chat):
    chat_id, user_id, headers = user_in_chat
    user_id = user_id + 'wrong_symbols'

    data = {'message': 'Hello, world!'}

    response = await api_client.post(MESSAGES_URL.format(chat_id) + f'?user_id={user_id}', headers=headers, json=data)
    assert response.status == HTTPStatus.NOT_FOUND


async def test_v1_create_without_user_id(api_client, auth_default_user, user_in_chat):
    chat_id, user_id, headers = user_in_chat

    data = {'message': 'Hello, world!'}

    response = await api_client.post(MESSAGES_URL.format(chat_id), headers=headers, json=data)
    assert response.status == HTTPStatus.BAD_REQUEST


async def test_v1_create_bad_chat_id(api_client, auth_default_user, user_in_chat):
    chat_id, user_id, headers = user_in_chat
    chat_id = chat_id + 'wrong_symbols'

    data = {'message': 'Hello, world!'}

    response = await api_client.post(MESSAGES_URL.format(chat_id) + f'?user_id={user_id}', headers=headers, json=data)
    assert response.status == HTTPStatus.NOT_FOUND


async def test_v1_get_bad_chat_id(api_client, auth_default_user, user_in_chat):
    chat_id, user_id, headers = user_in_chat
    chat_id = chat_id + 'wrong_symbols'

    limit = 1
    response = await api_client.get(MESSAGES_URL.format(chat_id) + f'?limit={limit}', headers=headers)
    assert response.status == HTTPStatus.NOT_FOUND


async def test_v1_get_bad_limit(api_client, auth_default_user, user_in_chat):
    chat_id, user_id, headers = user_in_chat

    limit = -1
    response = await api_client.get(MESSAGES_URL.format(chat_id) + f'?limit={limit}', headers=headers)
    assert response.status == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    ('message_count', 'limit', 'from_', 'correct_count'), [
        (10, 5, None, 5),
        (10, 7, 5, 5),
        (2, 3, None, 2),
    ]
)
async def test_v1_create_and_read(api_client, auth_default_user, user_in_chat, message_count, limit, from_,
                                  correct_count):
    chat_id, user_id, headers = user_in_chat

    for i in range(message_count):
        data = {'message': 'test' + str(i)}

        response = await api_client.post(MESSAGES_URL.format(chat_id) + f'?user_id={user_id}',
                                         headers=headers,
                                         json=data)
        assert response.status == HTTPStatus.CREATED

    if from_:
        additional_parameters = f'?limit={limit}&from={from_}'
    else:
        additional_parameters = f'?limit={limit}'
    response = await api_client.get(MESSAGES_URL.format(chat_id) + additional_parameters, headers=headers)
    assert response.status == HTTPStatus.OK

    body = await response.json()
    messages = body.get('messages')
    assert messages is not None
    assert len(messages) == correct_count

    next_ = body.get('next')
    assert next_ is not None
    assert next_ == {'iterator': str((from_ if from_ else 0) + correct_count)}
