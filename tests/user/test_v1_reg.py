import pytest
from http import HTTPStatus
from tests.conftest import REG_URL


@pytest.mark.parametrize(
    ('username', 'password'), [
        ('John Doe', '12345678'),
        ('Jane Doe', 'some_pass'),
        ('CyberneticLion', 'kitkat'),
    ]
)
async def test_v1_reg_create(api_client, username, password):
    data = {'user_name': username,
            'password': password}
    response = await api_client.post(REG_URL, json=data)
    assert response.status == HTTPStatus.CREATED


async def test_v1_reg_same_login(api_client):
    data = {'user_name': 'John Doe',
            'password': 'some_password'}
    response = await api_client.post(REG_URL, json=data)
    assert response.status == HTTPStatus.CREATED

    data['password'] = 'some_other_password'
    response = await api_client.post(REG_URL, json=data)
    assert response.status == HTTPStatus.CONFLICT


async def test_v1_reg_same_passwords(api_client):
    data = {'user_name': 'John Doe',
            'password': 'some_password'}
    response = await api_client.post(REG_URL, json=data)
    assert response.status == HTTPStatus.CREATED

    data['user_name'] = 'Jane Doe'
    response = await api_client.post(REG_URL, json=data)
    assert response.status == HTTPStatus.CREATED
