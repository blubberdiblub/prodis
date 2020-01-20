#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    Any as _Any,
    ContextManager as _ContextManager,
)

from contextlib import contextmanager as _contextmanager
from contextvars import ContextVar as _ContextVar


@_contextmanager
def let(var: _ContextVar, value: _Any) -> _ContextManager[None]:

    token = var.set(value)

    try:
        yield

    finally:
        var.reset(token)
