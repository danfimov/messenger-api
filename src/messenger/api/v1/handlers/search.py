from aiohttp.web import json_response, Response
from .base import BaseView
from ..models import SearchBeginRequest, SearchBeginResponse, \
    SearchTaskStatusRequest, SearchTaskStatusResponse, TaskStatus, \
    SearchResultRequest, SearchResultResponse
from ..errors import TaskNotFound, BadParametersError


class SearchBeginView(BaseView):
    URL_PATH = '/v1/chats/search'

    async def post(self) -> Response:
        body = await self.request.json()

        parsed_data = SearchBeginRequest.parse_obj(body)
        session_id = self.request.headers.get('session_id')
        user_id = await self.db_manager.get_user_id_from_session(session_id)
        new_task_id = await self.db_manager.create_task(
            message=parsed_data.message, user_id=user_id)
        return json_response(SearchBeginResponse(task_id=new_task_id).dict())


class SearchTaskStatusView(BaseView):
    URL_PATH = '/v1/chats/search/status/{task_id}'

    async def get(self) -> Response:
        parsed_data = SearchTaskStatusRequest(
            task_id=self.request.match_info['task_id']
        )

        session_id = self.request.headers.get('session_id')
        user_id = await self.db_manager.get_user_id_from_session(session_id)

        task_status = await self.db_manager.get_task_status(
            user_id=user_id,
            task_id=parsed_data.task_id
        )
        print(type(task_status))
        if task_status is None:
            return TaskNotFound()
        elif task_status == TaskStatus.waiting:
            return json_response(
                SearchTaskStatusResponse(status='waiting'))
        elif task_status == TaskStatus.in_progress:
            return json_response(
                SearchTaskStatusResponse(status='in-progress').dict())
        elif task_status == TaskStatus.done:
            return json_response(
                SearchTaskStatusResponse(status='done').dict())
        elif task_status == TaskStatus.failed:
            return json_response(
                SearchTaskStatusResponse(status='failed').dict())
        else:
            return json_response(
                SearchTaskStatusResponse(status=task_status).dict())


class SearchResultView(BaseView):
    URL_PATH = '/v1/chats/search/{task_id}/messages'

    async def get(self) -> Response:
        params = self.request.rel_url.query
        iterator = params.get('from')

        parsed_request = SearchResultRequest(
            task_id=self.request.match_info['task_id'],
            from_=iterator,
            **params
        )

        session_id = self.request.headers.get('session_id')
        user_id = await self.db_manager.get_user_id_from_session(session_id)

        status = await self.db_manager.get_task_status(
            task_id=parsed_request.task_id, user_id=user_id)
        if status is None:
            return TaskNotFound()
        elif status == TaskStatus.done:
            messages_ids = await self.db_manager.get_task_messages(
                task_id=parsed_request.task_id, user_id=user_id)

            if messages_ids is not None:
                result = await self.db_manager.get_messages_by_ids(
                    messages_ids=messages_ids,
                    limit=parsed_request.limit,
                    from_=parsed_request.from_
                )

                messages = []
                for elem in result:
                    messages.append({'text': elem[0], 'chat_id': elem[1]})

                iterator = parsed_request.from_ if parsed_request.from_ else 0
                iterator = {"iterator": str(len(messages) + iterator)}
            else:
                messages = []
                iterator = None

            return json_response(
                SearchResultResponse(
                    messages=messages,
                    next=iterator
                ).dict())

        elif status == TaskStatus.in_progress:
            return BadParametersError('task-in-progress')
        elif status == TaskStatus.waiting:
            return BadParametersError('task-in-progress')
        else:
            return TaskNotFound()
