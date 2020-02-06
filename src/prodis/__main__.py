#!/usr/bin/env python3

from typing import Optional as _Optional

import asyncio as _asyncio

from .clientlistener import ClientListener as _ClientListener

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


def main_runner(debug_asyncio: bool) -> None:

    create_from = [
        _ClientListener,
    ]

    tasks = [factory() for factory in create_from]
    _asyncio.run(main_coroutine(*tasks), debug=debug_asyncio)


def main(debug_asyncio: bool) -> _Optional[int]:

    try:
        main_runner(debug_asyncio)

    except _asyncio.CancelledError as exc:

        _log.exception("cancellation escaped main loop: {type}: {text}",
                       type=exc.__class__.__name__, text=str(exc))

        return 76

    except KeyboardInterrupt:

        return 130

    except Exception as exc:

        _log.exception("exception in main loop: {type}: {text}",
                       type=exc.__class__.__name__, text=str(exc))

        return 70

    except BaseException as exc:

        _log.exception("{type}: {text}",
                       type=exc.__class__.__name__, text=str(exc))

        raise

    return 0


if __name__ == '__main__':

    import sys as _sys

    from .debug import (
        DEBUG as _DEBUG,
        DEBUG_ASYNCIO as _DEBUG_ASYNCIO,
    )

    from . import logger as _logger
    _logger.basic_config(level=_logger.DEBUG if _DEBUG else _logger.NOTICE)

    _sys.exit(main(_DEBUG_ASYNCIO))
