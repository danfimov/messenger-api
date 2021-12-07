from aiohttp.web import run_app
from messenger.api.app import create_app


def main():
    app = create_app()
    run_app(
        app,
        host=app['SERVICE_HOST'],
        port=app['SERVICE_PORT'],
        access_log=app.logger
    )


if __name__ == '__main__':
    main()
