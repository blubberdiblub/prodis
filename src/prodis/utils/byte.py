#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    TypeAlias as _TypeAlias,
    TypeVar as _TypeVar,
)

from collections.abc import (
    Callable as _Callable,
    Generator as _Generator,
    Iterable as _Iterable,
    Iterator as _Iterator,
)

from struct import Struct as _Struct

from . import parse as _parse


_T = _TypeVar('_T')
_Requester: _TypeAlias = _Generator[int, bytes | bytearray, _T]


def _to_consumer(requester: _Requester,
                 mv: memoryview) -> tuple[_T, memoryview]:

    if not isinstance(mv, memoryview) or mv.itemsize != 1 or mv.ndim != 1:
        mv = memoryview(bytes(mv))

    to_send = None
    while True:
        try:
            num_bytes = requester.send(to_send)

        except StopIteration as exc:
            return exc.value, mv

        to_send = bytes(mv[:num_bytes])
        if len(to_send) < num_bytes:
            raise ValueError("end of data reached")

        mv = mv[num_bytes:]


def _to_parser(requester: _Requester,
               data: bytes | bytearray, start: int = 0) -> tuple[_T, int]:

    if not isinstance(data, (bytes, bytearray)):
        data = bytes(data)

    to_send = None
    while True:
        try:
            num_bytes = requester.send(to_send)

        except StopIteration as exc:
            return exc.value, start

        to_send = data[start:start + num_bytes]
        if len(to_send) < num_bytes:
            raise ValueError("end of data reached")

        start += num_bytes


def _to_converter(requester: _Requester, data: bytes | bytearray) -> _T:

    if not isinstance(data, (bytes, bytearray)):
        data = bytes(data)

    result, end = _to_parser(requester, data)
    if end < len(data):
        raise ValueError("data too long")

    return result


def consume_varint(mv: memoryview) -> tuple[int, memoryview]:

    return _to_consumer(_parse.request_varint(), mv)


def parse_varint(data: bytes | bytearray, start: int = 0) -> tuple[int, int]:

    return _to_parser(_parse.request_varint(), data, start=start)


def from_varint(data: bytes | bytearray) -> int:

    return _to_converter(_parse.request_varint(), data)


render_float = _Struct('>f').pack
render_double = _Struct('>d').pack


def render_varint(v: int) -> bytes:

    if 0 <= v <= 0x7f:
        return v.to_bytes(1, 'little')

    assert -0x80000000 <= v <= 0x7fffffff
    v &= 0xffffffff

    l = []

    while v >= 0x80:
        l.append(v & 0x7f | 0x80)
        v >>= 7

    return bytes(l + [v])


def render_varlong(v: int) -> bytes:

    if 0 <= v <= 0x7f:
        return v.to_bytes(1, 'little')

    assert -0x8000_0000_0000_0000 <= v <= 0x7fff_ffff_ffff_ffff
    v &= 0xffff_ffff_ffff_ffff

    l = []

    while v >= 0x80:
        l.append(v & 0x7f | 0x80)
        v >>= 7

    return bytes(l + [v])


def render_varbytes(b: bytes | bytearray) -> bytes:

    return render_varint(len(b)) + b


def render_varstr(s: str) -> bytes:

    b = s.encode()
    return render_varint(len(b)) + b


def render_identifier(namespace: str, name: str) -> bytes:

    if not namespace:
        namespace = 'minecraft'

    b = b'%b:%b' % (
        namespace.encode('ascii'),
        name.encode('ascii'),
    )
    return render_varint(len(b)) + b
