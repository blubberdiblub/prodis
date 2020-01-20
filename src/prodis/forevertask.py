#!/usr/bin/env python3

import asyncio as _asyncio


class ForeverTask:

    def __init__(self, loop: _asyncio.AbstractEventLoop = None) -> None:

        self._loop = loop
        self.future = None

    def schedule(self, loop: _asyncio.AbstractEventLoop = None) -> _asyncio.Future:

        if self.future is not None:
            raise ValueError("future already scheduled")

        if loop is None:
            loop = self._loop

            if loop is None:
                loop = _asyncio.get_event_loop()

        def clear_future(_) -> None:
            self.future = None

        future = self._get_future(loop=loop)
        future.add_done_callback(clear_future)
        self.future = future
        return future

    def _get_future(self, loop: _asyncio.AbstractEventLoop) -> _asyncio.Future:

        future = loop.create_future()
        future.set_result(True)
        return future
