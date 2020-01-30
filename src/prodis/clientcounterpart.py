#!/usr/bin/env python3

import asyncio as _asyncio
import sys as _sys

from .forevertask import ForeverTask as _ForeverTask
from .clienthandler import ClientHandler as _ClientHandler


class ClientListener(_ForeverTask):

    def _client_connected(
            self,
            reader: _asyncio.StreamReader,
            writer: _asyncio.StreamWriter,
    ) -> None:

        print("client connected", file=_sys.stderr, flush=True)

        client_handler = _ClientHandler(reader, writer)

        # noinspection PyUnreachableCode
        if __debug__:

            def stop_listener(task: _asyncio.Future) -> None:

                try:

                    exc = task.exception()

                except _asyncio.CancelledError as exc:

                    _dummy = 12345
                    pass

                if exc is not None:
                    self.future.cancel()

            client_handler.get_task().add_done_callback(stop_listener)

    async def _coroutine(self) -> None:

        loop = _asyncio.get_running_loop()

        server = await _asyncio.start_server(
            self._client_connected,
            host='localhost',
            port=25565,
            loop=loop,
        )

        if not server.sockets:
            raise ValueError("no sockets opened")

        return await server.serve_forever()

    def _get_future(self, loop) -> _asyncio.Task:

        return loop.create_task(self._coroutine())
