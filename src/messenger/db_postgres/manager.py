from os import environ
from datetime import datetime
from aiopg.sa import create_engine
from sqlalchemy import insert, select, delete, update, and_, func
from sqlalchemy.sql.ddl import CreateTable
from psycopg2.errors import UniqueViolation
from psycopg2 import OperationalError
from datetime import timedelta

from messenger.db_postgres.schema import users, chats, users_chats_relations, \
    messages, sessions, tasks


async def get_engine():
    engine = await create_engine(
        dsn=f"postgresql://{environ.get('POSTGRES_USER', 'username')}:"
            f"{environ.get('POSTGRES_PWD', 'hackme')}@"
            f"{environ.get('POSTGRES_HOST', 'localhost')}/"
            f"{environ.get('POSTGRES_DB', 'messenger')}")
    return engine


class DataBaseManager:
    # TODO: добаить декоратор для логгирования действий в базе
    _instance = None

    def __new__(cls, engine, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.engine = engine
        return cls._instance

    def __init__(self, engine):
        self.engine = engine

    @staticmethod
    async def ping_db() -> bool:
        """
        Проверяет, что бд доступна
        """
        try:
            engine = await get_engine()
            async with engine.acquire() as conn:
                await conn.execute("SELECT 1")
            engine.close()
            await engine.wait_closed()
            return True
        except (OSError, OperationalError,):
            return False

    async def create_user(self, user) -> bool:
        query = insert(users) \
            .values({"user_name": user.user_name, "password": user.password})
        try:
            async with self.engine.acquire() as cur:
                await cur.execute(query)
        except UniqueViolation:
            return False
        return True

    async def create_tables(self) -> None:
        """
        Создаёт все необходимые таблицы в базе данных, если таковых там еще нет
        """
        async with self.engine.acquire() as conn:
            await conn.execute(CreateTable(chats, if_not_exists=True))
            await conn.execute(CreateTable(users, if_not_exists=True))
            await conn.execute(CreateTable(messages, if_not_exists=True))
            await conn.execute(
                CreateTable(users_chats_relations, if_not_exists=True))
            await conn.execute(CreateTable(sessions, if_not_exists=True))
            await conn.execute(CreateTable(tasks, if_not_exists=True))

    async def is_chat_id_exist(self, chat_id: str) -> bool:
        """
        Проверяет наличие чата с нужным id в бд
        """
        query = select(chats) \
            .where(chats.c.chat_id == chat_id)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        return True if parsed_value else False

    async def is_rel_id_in_chat(self, chat_id: str, rel_id: str) -> bool:
        """
        Проверяет наличие связи между rel_id и чатом.

        (На уровне бизнес-логики: проверяет наличие пользователя в чате, так как мы отдаем rel_id при добалении
        пользователя в чат)
        """
        query = select(users_chats_relations) \
            .where(and_(users_chats_relations.c.chat_id == chat_id,
                        users_chats_relations.c.rel_id == rel_id))
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        return True if parsed_value else False

    async def is_user_id_in_chat(self, chat_id: str, user_id: str) -> bool:
        """
        Проверяет наличие связи между user_id и чатом.
        """
        query = select(users_chats_relations) \
            .where(and_(users_chats_relations.c.chat_id == chat_id,
                        users_chats_relations.c.user_id == user_id))
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        return True if parsed_value else False

    async def add_user_to_chat(self, chat_id: str, user_name: str,
                               user_id: str) -> str:
        """
        Добавляет пользователя в чат
        """
        query = insert(users_chats_relations) \
            .values(
            {'chat_id': chat_id, 'user_name': user_name, 'user_id': user_id}) \
            .returning(users_chats_relations.c.rel_id)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        return str(parsed_value[0])

    async def create_chat(self, chat_name: str) -> str:
        """
        Создаёт чат, используя введенное пользователем имя чата.
        """
        query = insert(chats) \
            .values({'chat_name': chat_name, 'created_at': datetime.utcnow()}) \
            .returning(chats.c.chat_id)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        return str(parsed_value[0])

    async def create_message(self, text: str, chat_id: str,
                             user_id: str) -> str:
        """
        Помещает сообщение пользователя в соответствующий чат
        """
        query = insert(messages) \
            .values({'text': text, 'chat_from': chat_id, 'user_from': user_id}) \
            .returning(messages.c.message_id)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        return str(parsed_value[0])

    async def get_messages(self, chat_id: str, limit: int,
                           from_: int = None) -> list:
        """
        Получает сообщения из чата
        """
        query = select(messages.c.text) \
            .where(messages.c.chat_from == chat_id) \
            .order_by(messages.c.created_at) \
            .limit(limit).offset(from_)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchall()
        if len(parsed_value) > 0:
            messages_text = [elem.as_tuple()[0] for elem in parsed_value]
            return messages_text
        return None

    async def get_messages_by_ids(self, messages_ids: list[str], limit: int,
                                  from_: int = None) -> list:
        """
        Получает сообщения из чата
        """
        query = select(messages.c.text, messages.c.chat_from) \
            .where(messages.c.message_id.in_(messages_ids)) \
            .order_by(messages.c.created_at) \
            .limit(limit).offset(from_)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchall()
        if len(parsed_value) > 0:
            messages_text = [elem.as_tuple()[:2] for elem in parsed_value]
            return messages_text
        return None

    async def authentication(self, user_name: str, password: str) -> str:
        """
        Проверяет данные для входа. При успешном нахождении данных в бд, возращает user_id, в противном случае - None
        """
        query = select(users.c.user_id) \
            .where(
            and_(users.c.user_name == user_name, users.c.password == password)) \
            .limit(1)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        res = parsed_value[0] if parsed_value else None
        return res

    async def create_session(self, user_id: str) -> str:
        query = insert(sessions) \
            .values({'user_id': user_id}) \
            .returning(sessions.c.session_id)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        return parsed_value[0]

    async def is_correct_session(self, session_id: str) -> bool:
        query = select(sessions) \
            .where(sessions.c.session_id == session_id) \
            .limit(1)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        return bool(parsed_value)

    async def delete_session(self, session_id: str) -> None:
        query = delete(sessions) \
            .where(sessions.c.session_id == session_id)
        async with self.engine.acquire() as conn:
            await conn.execute(query)

    async def get_user_id_from_session(self, session_id) -> str:
        query = select(sessions.c.user_id) \
            .where(sessions.c.session_id == session_id) \
            .limit(1)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        return parsed_value[0]

    async def create_task(self, message: str, user_id: str) -> str:
        """
        Создаёт задачу, используя введенное пользователем сообщение.
        """
        query = insert(tasks) \
            .values({'user_id': user_id, 'search_text': message,
                     'created_at': datetime.utcnow()}) \
            .returning(tasks.c.task_id)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        return str(parsed_value[0])

    async def get_task_status(self, user_id: str, task_id: str):
        query = select(tasks.c.status) \
            .where(
            and_(tasks.c.user_id == user_id, tasks.c.task_id == task_id)) \
            .limit(1)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        if parsed_value:
            return parsed_value[0]
        return None

    async def get_task_messages(self, user_id: str, task_id: str):
        query = select(tasks.c.messages) \
            .where(
            and_(tasks.c.user_id == user_id, tasks.c.task_id == task_id)) \
            .limit(1)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchone()
        if parsed_value:
            return parsed_value[0]
        return None

    async def delete_old_tasks(self):
        oldest_created_at = datetime.now() - timedelta(minutes=5)
        query = delete(tasks) \
            .filter(tasks.c.created_at > oldest_created_at).returning(
            tasks.c.task_id)
        async with self.engine.acquire() as conn:
            await conn.execute(query)

    async def restart_waiting_tasks(self):
        query = update(tasks) \
            .where(tasks.c.status == 1) \
            .values(status=0)
        async with self.engine.acquire() as conn:
            await conn.execute(query)

    async def get_unsolved_tasks(self):
        query = select(tasks).where(tasks.c.status == 0)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchall()
        return parsed_value

    async def change_task_status(self, new_status: int, task_id: str):
        query = update(tasks) \
            .where(tasks.c.task_id == task_id) \
            .values(status=new_status)
        async with self.engine.acquire() as conn:
            await conn.execute(query)

    async def get_all_user_chats(self, user_id: str):
        query = select(users_chats_relations.c.chat_id) \
            .where(users_chats_relations.c.user_id == user_id)
        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchall()
        return parsed_value

    async def find_messages(self, chats: list, search_text: str):
        query = select(messages.c.message_id) \
            .where(func.to_tsvector('russian',
                                    messages.c.text)
                   .match(search_text,
                          postgresql_regconfig='russian')) \
            .where(messages.c.chat_from.in_(chats)) \
            .order_by(messages.c.message_id.desc()) \
            .limit(100)

        async with self.engine.acquire() as conn:
            returning_value = await conn.execute(query)
            parsed_value = await returning_value.fetchall()
        return parsed_value

    async def add_finding_messages(self, task_id: str, messages: list):
        query = update(tasks) \
            .where(tasks.c.task_id == task_id) \
            .values(messages=messages)
        async with self.engine.acquire() as conn:
            await conn.execute(query)
