#!/usr/bin/env python3

import logging as _logging


[
    DEBUG,
    INFO,
    NOTICE,
    WARNING,
    ERROR,
    FATAL,
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
    FATAL: _logging.FATAL,
}


def basic_config(*, level: int = 0):

    """Configure logging"""

    level = max(min(level, FATAL), DEBUG)

    _logging.basicConfig(
        format='%(levelname)s: %(message)s' if level > DEBUG
               else '%(asctime)s %(levelname)s: %(message)s',
        level=_LEVEL_MAPPING[level],
    )


class Logger:

    """Should be instantiated by every module that wants to log something.

    By passing the module's `__name__`, it gets a logging hierarchy "for free".

    >>> from .logger import Logger
    >>> _log = Logger(__name__)
    >>> _log.notice("{culprit} twiddled too many knobs", culprit="foobar")
    """

    def __init__(self, module_name: str) -> None:

        self._log = _logging.getLogger(module_name)

    def debug(self, fmt: str, *args, **kwargs) -> None:

        if self._log.isEnabledFor(_LEVEL_MAPPING[DEBUG]):
            self._log.debug('%s', fmt.format(*args, **kwargs))

    def info(self, fmt: str, *args, **kwargs) -> None:

        if self._log.isEnabledFor(_LEVEL_MAPPING[INFO]):
            self._log.info('%s', fmt.format(*args, **kwargs))

    def notice(self, fmt: str, *args, **kwargs) -> None:

        if self._log.isEnabledFor(_LEVEL_MAPPING[NOTICE]):
            self._log.log(_LEVEL_MAPPING[NOTICE],
                          '%s', fmt.format(*args, **kwargs))

    def warning(self, fmt: str, *args, **kwargs) -> None:

        if self._log.isEnabledFor(_LEVEL_MAPPING[WARNING]):
            self._log.warning('%s', fmt.format(*args, **kwargs))

    def error(self, fmt: str, *args, **kwargs) -> None:

        if self._log.isEnabledFor(_LEVEL_MAPPING[ERROR]):
            self._log.error('%s', fmt.format(*args, **kwargs))

    def fatal(self, fmt: str, *args, **kwargs) -> None:

        if self._log.isEnabledFor(_LEVEL_MAPPING[FATAL]):
            self._log.fatal('%s', fmt.format(*args, **kwargs))

    def is_chatty(self) -> bool:

        return self._log.isEnabledFor(_LEVEL_MAPPING[NOTICE])

    def is_quiet(self) -> bool:

        return not self.is_chatty()

    def is_debug(self) -> bool:

        return self._log.isEnabledFor(_LEVEL_MAPPING[DEBUG])
