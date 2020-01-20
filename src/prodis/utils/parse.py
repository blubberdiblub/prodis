#!/usr/bin/env python3

from __future__ import annotations

from collections.abc import (
    Callable as _Callable,
    Generator as _Generator,
    Iterable as _Iterable,
    Iterator as _Iterator,
)


def request_varint() -> _Generator[int, bytes | bytearray, int]:

    octet, = yield 1
    if not octet & 0x80:
        return octet

    value = octet & 0x7f
    for shift in range(7, 28, 7):
        octet, = yield 1
        if not octet & 0x80:
            value |= octet << shift
            return value

        value |= (octet & 0x7f) << shift

    octet, = yield 1
    if octet > 0xf:
        raise ValueError("varint out of range")

    if octet & 0x8:
        octet |= -0x8

    return value | (octet << 28)


def request_varlong() -> _Generator[int, bytes | bytearray, int]:

    octet, = yield 1
    if not octet & 0x80:
        return octet

    value = octet & 0x7f
    for shift in range(7, 63, 7):
        octet, = yield 1
        if not octet & 0x80:
            value |= octet << shift
            return value

        value |= (octet & 0x7f) << shift

    octet, = yield 1
    if octet > 1:
        raise ValueError("varlong out of range")

    return value | -0x8000_0000_0000_0000 if octet else value


def request_varbytes() -> _Generator[int, bytes | bytearray, bytes]:

    n = yield from request_varint()
    return (yield n)


def request_varstr() -> _Generator[int, bytes | bytearray, str]:

    n = yield from request_varint()
    return (yield n).decode()


def request_identifier() -> _Generator[int, bytes | bytearray, tuple[str, str]]:

    n = yield from request_varint()
    match (yield n).decode('ascii').split(':'):
        case namespace, name:
            pass
        case name,:
            namespace = 'minecraft'
        case _:
            raise ValueError("identifier has more than 2 parts")

    return namespace, name
