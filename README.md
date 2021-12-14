# Бэкенд для мессенджера

[![Flake8](https://github.com/LoveSolaristics/messenger-api/actions/workflows/flake8.yml/badge.svg?branch=master)](https://github.com/LoveSolaristics/messenger-api/actions/workflows/flake8.yml)
[![Pytest](https://github.com/LoveSolaristics/messenger-api/actions/workflows/pytest.yml/badge.svg?branch=master)](https://github.com/LoveSolaristics/messenger-api/actions/workflows/pytest.yml)

Это учебный проект, начало которому было положено в ШБР Яндекса. 
Данный проект реализует REST-API для мессенджера. 

## Реализованные функции 

Пользователь может:

- регистрироваться, получая токен
- создавать и входить в чаты 
- писать в чат / получать сообщение с пагинацией
- искать по чатам (задача асинхронная, на запрос поиска пользователь получает id задачи)

## Используемые технологии

1. Для реализации api была использована библиотека `aiohttp`. 
2. На данный момент валидация запросов осуществляется с помощью библиотеки `pydantic`. 
3. Взаимодействие с базой данных `PostgreSQL` происходит посредством `SQLAlchemy ORM`. 
4. Асинхронные таски используют библиотеку `asyncio`.
5. Настроены автотесты (`pytest`) и проверка процента покрытия кода тестами, а также запуск линтера (`flake8`) при коммите.

## Локальный запуск

Запуск приложения напрямую:

```commandline
python src/messenger/api/__main__.py
```

Установка пакета и запуск:

```commandline
pip install src/
```

```commandline
messenger-api
```

Запуск тестов:

```commandline
pytest tests
```

После запуска тестов можно увидеть подробный отчет о покрытие кода тестами в файле `htmlcov/index.html`.