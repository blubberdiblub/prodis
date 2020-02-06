#!/usr/bin/env python3

from typing import Optional as _Optional

import asyncio as _asyncio

from .runner import run as _run

from .logger import Logger as _Logger
_log = _Logger(__name__)


def main(debug_asyncio: bool = False) -> _Optional[int]:

    try:
        _run(debug_asyncio)

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
