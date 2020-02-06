#!/usr/bin/env python3

import asyncio as _asyncio

from .debug import DEBUG_ASYNCIO as _DEBUG_ASYNCIO

from .forevertask import ForeverTask as _ForeverTask
from .clienthandler import ClientHandler as _ClientHandler

from .logger import Logger as _Logger
_log = _Logger(__name__)


class ClientListener(_ForeverTask):

    def __init__(self, host: str = 'localhost', port: int = 25565) -> None:

        super().__init__()

        self.host = host
        self.port = port

        self.server = None

    def _client_connected(
            self,
            reader: _asyncio.StreamReader,
            writer: _asyncio.StreamWriter,
    ) -> None:

        _log.notice("client connected")

        client_handler = _ClientHandler(reader, writer)

        if _DEBUG_ASYNCIO:

            def stop_listener(task: _ClientHandler) -> None:

                if task.exception() is not None:
                    self.server.close()

            client_handler.add_done_callback(stop_listener)

    async def _coroutine(self) -> None:

        self.server = await _asyncio.start_server(
            self._client_connected,
            host=self.host,
            port=self.port,
            start_serving=False,
        )

        if not self.server.sockets:
            raise ValueError("no sockets opened")

        try:
            await self.server.serve_forever()

        except _asyncio.CancelledError:

            _log.debug("ClientListener was cancelled")

        else:

            _log.debug("ClientListener finished")

        return

    def _get_future(self, loop: _asyncio.AbstractEventLoop) -> _asyncio.Task:

        return loop.create_task(self._coroutine())
