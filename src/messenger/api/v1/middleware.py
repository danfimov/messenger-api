from aiohttp.web import middleware, Response, Request
from typing import Callable
from pydantic import ValidationError
from os import environ

from messenger.api.v1.errors import BadParametersError, MethodNotAllowed, \
    AuthorizationRequired, UserNotFound


@middleware
async def error_solving(request: Request, handler: Callable) -> Response:
    try:
        request.app['log_manager'].logger.debug(
            f'Handler "{handler.__name__}" has been activated.')
        response = await handler(request)
        request.app['log_manager'].logger.debug(
            f'Handler "{handler.__name__}" is finish his work.')
        return response
    except (ValueError, KeyError, ValidationError) as err:
        request.app['log_manager'].log_error(err)
        return BadParametersError('Параметры запроса неверны')
    except Exception as err:
        request.app['log_manager'].log_error(err)
        return MethodNotAllowed('Неверный адрес или метод в запросе')


@middleware
async def authorization(request: Request, handler: Callable):
    not_required = ['AuthenticationView', 'RegistrationView', 'PingDbView',
                    'PingView']

    request.app['log_manager'].logger.debug(
        'Authorization process has been activated.')
    if handler.__name__ in not_required or environ.get("AUTH_DISABLED", False):
        request.app['log_manager'].logger.debug('Authorization skipped.')
        return await handler(request)
    else:
        session_id = request.headers.get('session_id')
        if session_id:
            is_correct = await request.app['db_manager'].is_correct_session(
                session_id)
            if is_correct:
                request.app['log_manager'].logger.debug(
                    'Authorization passed.')
                return await handler(request)
            else:
                request.app['log_manager'].logger.debug('User not found.')
                return UserNotFound()
        request.app['log_manager'].logger.debug('Authorization required.')
        return AuthorizationRequired()
