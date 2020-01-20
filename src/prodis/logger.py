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


class _LogRecord(_logging.LogRecord):

    def __init__(self, name: str, level: int, pathname: str, lineno: int,
                 msg: str, kwargs,
                 exc_info, func=None, sinfo=None, style='%') -> None:

        if style not in ['%', '{']:
            raise ValueError(f"unknown style {style!r}")

        super().__init__(name, level, pathname, lineno, str(msg), (), exc_info,
                         func=func, sinfo=sinfo)

        self.args = kwargs
        self.__style = style

    def getMessage(self) -> str:

        if self.__style == '%':
            return self.msg % self.args

        return self.msg.format(**self.args)


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

    >>> from .logger import Logger
    >>> log = Logger(__name__)
    >>> log.notice("{culprit} twiddled too many knobs", culprit="foobar")
    """

    def __init__(self, module_name: str) -> None:

        self._logger = _logging.getLogger(module_name)

    def debug(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            style='{', **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[DEBUG], msg, exc_info, stack_info, stacklevel,
                  style, **kwargs)

    def info(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            style='{', **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[INFO], msg, exc_info, stack_info, stacklevel,
                  style, **kwargs)

    def notice(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            style='{', **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[NOTICE], msg, exc_info, stack_info, stacklevel,
                  style, **kwargs)

    def warning(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            style='{', **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[WARNING], msg, exc_info, stack_info,
                  stacklevel, style, **kwargs)

    def error(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            style='{', **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[ERROR], msg, exc_info, stack_info, stacklevel,
                  style, **kwargs)

    def critical(
            self, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            style='{', **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[CRITICAL], msg, exc_info, stack_info,
                  stacklevel, style, **kwargs)

    def log(
            self, level: int, msg: str,
            exc_info=None, stack_info: bool = False, stacklevel: int = 1,
            style='{', **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[level], msg, exc_info, stack_info, stacklevel,
                  style, **kwargs)

    def exception(
            self, msg: str,
            exc_info=True, stack_info: bool = True, stacklevel: int = 1,
            style='{', **kwargs,
    ) -> None:

        self._log(_LEVEL_MAPPING[ERROR], msg, exc_info, stack_info, stacklevel,
                  style, **kwargs)

    def _log(self, mapped: int, msg: str, exc_info, stack_info: bool,
             stacklevel: int, style: str, **kwargs) -> None:

        if self._logger.isEnabledFor(mapped):

            # noinspection PyArgumentList
            fn, lno, func, sinfo = self._logger.findCaller(stack_info,
                                                           max(stacklevel, 1))

            if exc_info:
                if isinstance(exc_info, BaseException):
                    exc_info = type(exc_info), exc_info, exc_info.__traceback__
                elif not isinstance(exc_info, tuple):
                    import sys
                    exc_info = sys.exc_info()

            record = _LogRecord(self._logger.name, mapped, fn, lno, msg, kwargs,
                                exc_info, func=func, sinfo=sinfo, style=style)

            self._logger.handle(record)

    def is_chatty(self) -> bool:

        return self._logger.isEnabledFor(_LEVEL_MAPPING[NOTICE])

    def is_quiet(self) -> bool:

        return not self.is_chatty()

    def is_debug(self) -> bool:

        return self._logger.isEnabledFor(_LEVEL_MAPPING[DEBUG])
