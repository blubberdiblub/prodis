#!/usr/bin/env python3

from typing import (
    Callable as _Callable,
    Iterable as _Iterable,
    Iterator as _Iterator,
    Tuple as _Tuple,
)

from functools import partial as _partial
from itertools import islice as _islice


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


def consume_string(it: _Iterator[int]) -> str:

    n = consume_varint(it)
    return bytes(_islice(it, n)).decode()


def consume_identifier(it: _Iterator[int]) -> _Tuple[str, str]:

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


def produce_string(s: str) -> _Iterator[int]:

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
