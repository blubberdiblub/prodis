#!/usr/bin/env python3

import trio as _trio

from .runner import main_coroutine

from .logger import Logger as _Logger
_log = _Logger(__name__)


def main() -> int | None:

    try:
        _trio.run(main_coroutine,
                  restrict_keyboard_interrupt_to_checkpoints=True)

    except _trio.Cancelled as exc:

        _log.exception("cancellation escaped main loop: {type}: {text}",
                       type=type(exc).__name__, text=str(exc))

        return 76

    except KeyboardInterrupt:

        return 130

    except Exception as exc:

        _log.exception("exception in main loop: {type}: {text}",
                       type=type(exc).__name__, text=str(exc),
                       stack_info=False)

        return 70

    except BaseException as exc:

        _log.exception("{type}: {text}",
                       type=exc.__class__.__name__, text=str(exc))

        raise

    return 0
