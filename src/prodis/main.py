#!/usr/bin/env python3

import asyncio as _asyncio

from .clientcounterpart import ClientListener as _ClientListener


async def main_coroutine(*tasks) -> None:

    futures = [task.schedule() for task in tasks]
    done, pending = await _asyncio.wait(futures,
                                        return_when=_asyncio.FIRST_EXCEPTION)

    for future in pending:
        future.cancel()

    for future in done:
        try:
            future.result()

        except _asyncio.CancelledError:

            pass


def main() -> None:

    create_from = [
        _ClientListener,
    ]

    tasks = [factory() for factory in create_from]
    _asyncio.run(main_coroutine(*tasks))


if __name__ == '__main__':
    import sys as _sys

    from . import logger as _logger
    _logger.basic_config(level=_logger.DEBUG if __debug__ or _sys.flags.dev_mode
                         else _logger.NOTICE)
    _log = _logger.Logger(__name__)

    try:
        main()

    except _asyncio.CancelledError as exc:

        _log.exception("cancellation escaped main loop: {type}: {text}",
                       type=exc.__class__.__name__, text=str(exc))
        _sys.exit(1)

    except Exception as exc:

        _log.exception("exception in main loop: {type}: {text}",
                       type=exc.__class__.__name__, text=str(exc))
        _sys.exit(1)

    except BaseException as exc:

        _log.exception("{type}: {text}",
                       type=exc.__class__.__name__, text=str(exc))

        raise
