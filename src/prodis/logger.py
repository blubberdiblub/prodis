#!/usr/bin/env python3

import logging as _logging


[
    DEBUG,
    INFO,
    NOTICE,
    WARNING,
    ERROR,
    CRITICAL,
] = range(6)


def _get_or_add_level(name: str, level: int) -> int:

    try:

        level = getattr(_logging, name)

    except AttributeError:

        if not isinstance(level, int):

            raise TypeError("level must be an int")

        _logging.addLevelName(level, name)

        if name.isidentifier() and name.isupper():
            setattr(_logging, name, level)

    else:

        if not isinstance(level, int):

            raise NameError("level name collides with other logging attribute")

    return level


_LEVEL_MAPPING = {
    DEBUG: _logging.DEBUG,
    INFO: _logging.INFO,
    NOTICE: _get_or_add_level('NOTICE', (_logging.INFO + _logging.WARN) // 2),
    WARNING: _logging.WARNING,
    ERROR: _logging.ERROR,
    CRITICAL: _logging.CRITICAL,
}


def basic_config(*, level: int = 0):

    """Configure logging"""

    level = max(min(level, CRITICAL), DEBUG)

    _logging.basicConfig(
        format='%(levelname)s: %(message)s' if level > DEBUG
               else '%(asctime)s %(levelname)s: %(message)s',
        level=_LEVEL_MAPPING[level],
    )


class Logger:

    """Should be instantiated by every module that wants to log something.

    By passing the module's `__name__`, it gets a logging hierarchy "for free".

    >>> from prodis.logger import Logger
    >>> log = Logger(__name__)
    >>> log.notice("{culprit} twiddled too many knobs", culprit="foobar")
    """

    def __init__(self, module_name: str) -> None:

        self._logger = _logging.getLogger(module_name)

    def debug(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[DEBUG], msg, exc_info=exc_info,
                  stack_info=stack_info, stacklevel=stacklevel, **kwargs)

    def info(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[INFO], msg, exc_info=exc_info,
                  stack_info=stack_info, stacklevel=stacklevel, **kwargs)

    def notice(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[NOTICE], msg, exc_info=exc_info,
                  stack_info=stack_info, stacklevel=stacklevel, **kwargs)

    def warning(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[WARNING], msg, exc_info=exc_info,
                  stack_info=stack_info, stacklevel=stacklevel, **kwargs)

    def error(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[ERROR], msg, exc_info=exc_info,
                  stack_info=stack_info, stacklevel=stacklevel, **kwargs)

    def critical(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[CRITICAL], msg, exc_info=exc_info,
                  stack_info=stack_info, stacklevel=stacklevel, **kwargs)

    def log(
            self, level: int, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[level], msg, exc_info=exc_info,
                  stack_info=stack_info, stacklevel=stacklevel, **kwargs)

    def exception(
            self, msg: str,
            stack_info: bool = True, stacklevel: int = 1,
            **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[ERROR], msg, exc_info=True,
                  stack_info=stack_info, stacklevel=stacklevel, **kwargs)

    def _log(self, mapped: int, msg: str, exc_info, stack_info: bool,
             stacklevel: int, **kwargs) -> None:

        if self._logger.isEnabledFor(mapped):

            self._logger.log(
                mapped, msg, kwargs, extra=kwargs,
                exc_info=exc_info, stack_info=stack_info,
                stacklevel=max(stacklevel, 1) + 2,
            )

    def is_chatty(self) -> bool:

        return self._logger.isEnabledFor(_LEVEL_MAPPING[NOTICE])

    def is_quiet(self) -> bool:

        return not self.is_chatty()

    def is_debug(self) -> bool:

        return self._logger.isEnabledFor(_LEVEL_MAPPING[DEBUG])
