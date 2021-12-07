from http import HTTPStatus
from tests.conftest import REG_URL, AUTH_URL, CREATE_CHAT_URL, ADD_USER_URL, MESSAGES_URL, QUIT_URL

FIRST_USER = {
    'user_name': 'user1',
    'password': 'password'
}
SECOND_USER = {
    'user_name': 'user2',
    'password': 'password'
}


async def test_v1_two_users(api_client):
    """
    Создаем двух пользователей, авторизируем, помещаем в один чат, создаем и получаем ссообщения
    """

    # регистрация

    data_1 = FIRST_USER
    response = await api_client.post(REG_URL, json=data_1)
    assert response.status == HTTPStatus.CREATED

    data_2 = SECOND_USER
    response = await api_client.post(REG_URL, json=data_2)
    assert response.status == HTTPStatus.CREATED

    # авторизация

    response = await api_client.get(AUTH_URL, json=data_1)
    assert response.status == HTTPStatus.OK
    body_1 = await response.json()
    session_id_1 = body_1['session_id']

    response = await api_client.get(AUTH_URL, json=data_2)
    assert response.status == HTTPStatus.OK
    body_2 = await response.json()
    session_id_2 = body_2['session_id']

    assert session_id_2 != session_id_1

    # создание чата

    headers = {'session_id': session_id_1}
    data = {'chat_name': 'new test chat'}

    response = await api_client.post(CREATE_CHAT_URL, json=data, headers=headers)
    assert response.status == HTTPStatus.CREATED

    body = await response.json()
    chat_id = body.get('chat_id', None)
    assert chat_id is not None

    # добавление пользователей в чат

    headers_1 = {'session_id': session_id_1}
    data = {"user_name": "Вася Пупкин"}
    response = await api_client.post(ADD_USER_URL.format(chat_id), json=data, headers=headers_1)
    assert response.status == HTTPStatus.CREATED

    body = await response.json()
    user_id_1 = body.get('user_id', None)
    assert user_id_1 is not None

    headers_2 = {'session_id': session_id_2}
    data = {"user_name": "Юлиана Мирославская"}
    response = await api_client.post(ADD_USER_URL.format(chat_id), json=data, headers=headers_2)
    body = await response.json()
    assert response.status == HTTPStatus.CREATED

    body = await response.json()
    user_id_2 = body.get('user_id', None)
    assert user_id_2 is not None

    # попеременное добавление сообщений

    data = {'message': 'Hello!'}
    response = await api_client.post(MESSAGES_URL.format(chat_id) + f'?user_id={user_id_1}',
                                     headers=headers_1,
                                     json=data)
    assert response.status == HTTPStatus.CREATED

    data = {'message': 'Hello, how are you?'}
    response = await api_client.post(MESSAGES_URL.format(chat_id) + f'?user_id={user_id_2}',
                                     headers=headers_2,
                                     json=data)
    assert response.status == HTTPStatus.CREATED

    data = {'message': "I'm fine, thanks)"}
    response = await api_client.post(MESSAGES_URL.format(chat_id) + f'?user_id={user_id_1}',
                                     headers=headers_1,
                                     json=data)
    assert response.status == HTTPStatus.CREATED

    # считывание сообщений первым пользователем

    limit = 3
    response = await api_client.get(MESSAGES_URL.format(chat_id) + f'?limit={limit}', headers=headers_1)
    assert response.status == HTTPStatus.OK

    body = await response.json()
    messages = body.get('messages')
    assert messages is not None
    assert len(messages) == 3

    next_ = body.get('next')
    assert next_ is not None
    assert next_ == {'iterator': '3'}

    # считывание сообщений вторым пользователем

    limit = 10
    response = await api_client.get(MESSAGES_URL.format(chat_id) + f'?limit={limit}', headers=headers_2)
    assert response.status == HTTPStatus.OK

    body = await response.json()
    messages = body.get('messages')
    assert messages is not None
    assert len(messages) == 3

    next_ = body.get('next')
    assert next_ is not None
    assert next_ == {'iterator': '3'}

    # выход

    response = await api_client.post(QUIT_URL, headers={'session_id': session_id_1})
    assert response.status == HTTPStatus.OK

    response = await api_client.post(QUIT_URL, headers={'session_id': session_id_2})
    assert response.status == HTTPStatus.OK
