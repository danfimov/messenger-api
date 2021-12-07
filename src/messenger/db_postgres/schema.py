from uuid import uuid1
from datetime import datetime
from sqlalchemy import Table, String, MetaData, Column, DateTime, Text, BigInteger, ARRAY, Integer
from ..api.v1.models import TaskStatus

# SQLAlchemy рекомендует использовать единый формат для генерации названий для
# индексов и внешних ключей.
# https://docs.sqlalchemy.org/en/13/core/constraints.html#configuring-constraint-naming-conventions
convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)

users = Table(
    "users",
    metadata,
    Column("user_id", String, default=uuid1, unique=True, primary_key=True),
    Column("user_name", String(255), unique=True, nullable=False),
    Column("password", String(255), nullable=False),
    Column("created_at", DateTime(timezone=True),
           default=datetime.now(), nullable=False),
)

chats = Table(
    "chats",
    metadata,
    Column("chat_id", String, default=uuid1, primary_key=True),
    Column("chat_name", String(255), nullable=False),
    Column("created_at", DateTime(timezone=True), default=datetime.now(),
           nullable=False),
)

users_chats_relations = Table(
    "users_chats_relations",
    metadata,
    Column('rel_id', String, default=uuid1, primary_key=True),
    Column("user_id", String, nullable=False),
    Column("user_name", String(255), nullable=False),
    Column("chat_id", String, nullable=False),
)

sessions = Table(
    "sessions",
    metadata,
    Column('rel_id', BigInteger, autoincrement=True, nullable=False, primary_key=True),
    Column("user_id", String, nullable=False),
    Column('session_id', String, default=uuid1, nullable=False)
)

messages = Table(
    "messages",
    metadata,
    Column("message_id", String, default=uuid1, primary_key=True),
    Column("user_from", String, nullable=False),
    Column("chat_from", String, nullable=False),
    Column('text', Text, nullable=False),
    Column("created_at", DateTime(timezone=True), default=datetime.now(),
           nullable=False),
)

tasks = Table(
    "tasks",
    metadata,
    Column("task_id", String, default=uuid1, primary_key=True),
    Column("user_id", String, nullable=False),
    Column("search_text", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), default=datetime.now(),
           nullable=False),
    Column('status', Integer, nullable=False, default=TaskStatus.waiting),
    Column('messages', ARRAY(String, dimensions=1), default=[],
           nullable=False)
)
