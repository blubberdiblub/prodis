#!/usr/bin/env python3

import asyncio as _asyncio

from .forevertask import ForeverTask as _ForeverTask
from .clienthandler import ClientHandler as _ClientHandler

from .logger import Logger as _Logger
_log = _Logger(__name__)


class ClientListener(_ForeverTask):

    def _client_connected(
            self,
            reader: _asyncio.StreamReader,
            writer: _asyncio.StreamWriter,
    ) -> None:

        _log.notice("client connected")

        client_handler = _ClientHandler(reader, writer)

        # noinspection PyUnreachableCode
        if __debug__:

            def stop_listener(task: _asyncio.Future) -> None:

                try:

                    exc = task.exception()

                except _asyncio.CancelledError as exc:

                    _log.debug("ClientHandler was cancelled")
                    _dummy = 12345
                    pass

                if exc is not None:
                    _log.exception(
                        "exception occurred in ClientHandler: {type}: {text}",
                        type=exc.__class__.__name__, text=str(exc),
                        exc_info=exc, stack_info=False,
                    )
                    self.future.cancel()
                    raise exc

            client_handler.get_task().add_done_callback(stop_listener)

    async def _coroutine(self) -> None:

        server = await _asyncio.start_server(
            self._client_connected,
            host='localhost',
            port=25565,
        )

        if not server.sockets:
            raise ValueError("no sockets opened")

        try:
            await self.server.serve_forever()

        except _asyncio.CancelledError:

            _log.debug("ClientListener was cancelled")

        else:

            _log.debug("ClientListener finished")

        return

    def _get_future(self, loop) -> _asyncio.Task:

        return loop.create_task(self._coroutine())
