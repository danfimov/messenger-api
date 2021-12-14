from aiohttp.web import Application
from asyncio import create_task, sleep
from aiohttp_pydantic import oas

from messenger.api.log import LogManager
from messenger.api.v1.handlers import HANDLERS
from messenger.api.v1.middleware import error_solving, authorization
from messenger.db_postgres.manager import DataBaseManager, get_engine
from messenger.api.v1.models import TaskStatus


def setup_routes(app: Application):
    for handler in HANDLERS:
        app.router.add_route('*', handler.URL_PATH, handler)


async def init_database(app) -> None:
    engine = await get_engine()
    app['db_manager'] = DataBaseManager(engine)
    await app['db_manager'].create_tables()


async def task_cleaner(app) -> None:
    try:
        while True:
            await app['db_manager'].delete_old_tasks()
            await sleep(60)  # чистим список задач каждую минуту
    except Exception as e:
        app['log_manager'].logger\
            .error(f'Task cleaner is stopped with an error: {e}')


async def task_executor(app) -> None:
    try:
        while True:
            tasks = await app['db_manager'].get_unsolved_tasks()
            if not tasks:
                await sleep(1)
                continue

            for task in tasks:
                task_id, user_id, search_text = task[0], task[1], task[2]
                await app['db_manager'].change_task_status(
                    task_id=task_id,
                    new_status=TaskStatus.in_progress
                )

                chats = [elem[0] for elem in
                         await app['db_manager'].get_all_user_chats(
                             user_id=user_id)]
                if chats:
                    messages = [
                        elem[0] for elem in
                        await app['db_manager'].find_messages(
                            chats=chats, search_text=search_text)
                    ]
                    await app['db_manager'].add_finding_messages(
                        task_id=task_id,
                        messages=messages
                    )

                await app['db_manager'].change_task_status(
                    task_id=task_id,
                    new_status=TaskStatus.done
                )
    except Exception as e:
        app['log_manager'].logger.\
            error(f'Task executor is stopped with an error: {e.args}')


async def start_task_processing(app) -> None:
    """
    Запускает все процессы связанные, с обработкой задач по поиску
    """
    await app['db_manager'].restart_waiting_tasks()
    create_task(task_cleaner(app))
    create_task(task_executor(app))


async def close_database(app: Application) -> None:
    app['db_manager'].engine.close()
    await app['db_manager'].engine.wait_closed()


def create_app() -> Application:
    log_manager = LogManager()
    logger = log_manager.logger

    app = Application(
        middlewares=[authorization, error_solving, ],
        logger=logger
    )

    setup_routes(app)

    oas.setup(app, url_prefix='/spec-api', title_spec="Messenger API",
              version_spec="0.0.1")

    app['log_manager'] = log_manager

    app['SERVICE_HOST'] = '0.0.0.0'
    app['SERVICE_PORT'] = '8080'

    app.on_startup.extend([init_database, start_task_processing])
    app.on_cleanup.extend([close_database])

    return app
