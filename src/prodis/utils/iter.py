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

from itertools import islice as _islice
from struct import Struct as _Struct

from . import parse as _parse


_T = _TypeVar('_T')
_Requester: _TypeAlias = _Generator[int, bytes | bytearray, _T]


def _to_consumer(requester: _Requester, it: _Iterator[int]) -> _T:

    if not isinstance(it, _Iterator):
        it = iter(it)

    to_send = None
    while True:
        try:
            num_bytes = requester.send(to_send)

        except StopIteration as exc:
            return exc.value

        to_send = bytes(_islice(it, num_bytes))
        if len(to_send) < num_bytes:
            raise ValueError("iterator exhausted")


def _to_parser(requester: _Requester,
               it: _Iterator[int], start: int = 0) -> tuple[_T, int]:

    if not isinstance(it, _Iterator):
        it = iter(it)

    if start:
        () = _islice(it, start, start)

    to_send = None
    while True:
        try:
            num_bytes = requester.send(to_send)

        except StopIteration as exc:
            return exc.value, start

        to_send = bytes(_islice(it, num_bytes))
        if len(to_send) < num_bytes:
            raise ValueError("iterator exhausted")

        start += num_bytes


def _to_converter(requester: _Requester, it: _Iterator[int]) -> _T:

    if not isinstance(it, _Iterator):
        it = iter(it)

    result = _to_consumer(requester, it)
    () = it

    return result


_STRUCT_FLOAT = _Struct('>f')
_STRUCT_DOUBLE = _Struct('>d')


def consume_float(it: _Iterator[int]) -> float:

    f, = _STRUCT_FLOAT.unpack(bytes(_islice(it, 4)))
    return f


def consume_double(it: _Iterator[int]) -> float:

    d, = _STRUCT_DOUBLE.unpack(bytes(_islice(it, 8)))
    return d


def consume_varint(it: _Iterator[int]) -> int:

    octet = next(it)
    if not octet & 0x80:
        return octet

    value = octet & 0x7f
    shift = 7
    for octet in it:
        if not octet & 0x80:
            value |= octet << shift
            break
        value |= (octet & 0x7f) << shift
        shift += 7
        if shift >= 32:
            raise ValueError("varint too long")
    else:
        raise ValueError("iterator exhausted before end of varint")

    if shift == 28:
        if octet > 0xf:
            raise ValueError("varint out of range")
        if octet & 0x8:
            return value | -0x80000000

    return value


def consume_varlong(it: _Iterator[int]) -> int:

    return _to_consumer(_parse.request_varlong(), it)


def consume_varbytes(it: _Iterator[int]) -> bytes:

    return _to_consumer(_parse.request_varbytes(), it)


def consume_varstr(it: _Iterator[int]) -> str:

    n = consume_varint(it)
    return bytes(_islice(it, n)).decode()


def consume_identifier(it: _Iterator[int]) -> tuple[str, str]:

    n = consume_varint(it)
    namespace, _, name = bytes(_islice(it, n)).rpartition(b':')

    if not namespace:
        return 'minecraft', name.decode('ascii')

    return namespace.decode('ascii'), name.decode('ascii')


def produce_varint(v: int) -> _Iterator[int]:

    if 0 <= v <= 0x7f:
        yield v
        return

    assert -0x80000000 <= v <= 0x7fffffff
    v &= 0xffffffff

    while v >= 0x80:
        yield v & 0x7f | 0x80
        v >>= 7

    yield v


def produce_varbytes(b: bytes | bytearray) -> _Iterator[int]:

    yield from produce_varint(len(b))
    yield from b


def produce_varstr(s: str) -> _Iterator[int]:

    b = s.encode()
    yield from produce_varint(len(b))
    yield from b


def produce_identifier(namespace: str, name: str) -> _Iterator[int]:

    if not namespace:
        namespace = 'minecraft'

    b = b'%b:%b' % (
        namespace.encode('ascii'),
        name.encode('ascii'),
    )
    yield from produce_varint(len(b))
    yield from b
