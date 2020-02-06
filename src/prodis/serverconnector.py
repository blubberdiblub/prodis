#!/usr/bin/env python3

import asyncio as _asyncio

from .debug import DEBUG_ASYNCIO as _DEBUG_ASYNCIO

from .forevertask import ForeverTask as _ForeverTask
from .clienthandler import ClientHandler as _ClientHandler

from .logger import Logger as _Logger
_log = _Logger(__name__)


class ServerConnector(_ForeverTask):

    def __init__(self, host: str = 'localhost', port: int = 14454,
                 retry_delay: int = 3, reconnect_delay: int = 1) -> None:

        super().__init__()

        self.host = host
        self.port = port
        self.retry_delay = retry_delay
        self.reconnect_delay = reconnect_delay

    async def _coroutine(self) -> None:

        while True:

            try:
                reader, writer = await _asyncio.open_connection(
                    host=self.host,
                    port=self.port,
                )

            except ConnectionError:

                await _asyncio.sleep(self.retry_delay)
                continue

            await _asyncio.sleep(self.reconnect_delay)

    def _get_future(self, loop: _asyncio.AbstractEventLoop) -> _asyncio.Task:

        return loop.create_task(self._coroutine())
