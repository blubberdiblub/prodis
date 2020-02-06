#!/usr/bin/env python3

import asyncio as _asyncio

from .clientlistener import ClientListener as _ClientListener
from .serverconnector import ServerConnector as _ServerConnector

from .logger import Logger as _Logger
_log = _Logger(__name__)


async def main_coroutine(*tasks) -> None:

    futures = [task.schedule() for task in tasks]
    done, pending = await _asyncio.wait(futures,
                                        return_when=_asyncio.FIRST_EXCEPTION)

    for future in pending:

        try:

            future.cancel()

        except BaseException as exc:

            _log.exception("cancelling future resulted in: {type}: {text}",
                           type=exc.__class__.__name__, text=str(exc))
            raise

    for future in done:
        try:
            future.result()

        except _asyncio.CancelledError:

            pass


def run(debug_asyncio: bool) -> None:

    create_from = [
        _ClientListener,
        _ServerConnector,
    ]

    tasks = [factory() for factory in create_from]
    _asyncio.run(main_coroutine(*tasks), debug=debug_asyncio)
