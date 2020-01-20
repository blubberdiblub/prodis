#!/usr/bin/env python3

from __future__ import annotations

from collections.abc import (
    Iterator as _Iterator,
)

from ..packet import MinecraftPacketWithID as _MinecraftPacketWithID


class Packet(_MinecraftPacketWithID):

    pass


class Request(Packet):

    id = 0x0

    def __init__(self) -> None:

        super().__init__()

    def __getstate__(self) -> dict[str, object]:

        return {}

    @property
    def payload(self) -> bytes | bytearray:

        return b''

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        () = it


# noinspection DuplicatedCode
class Ping(Packet):

    id = 0x1

    def __init__(self, value: float = 0) -> None:

        super().__init__()

        self.value = value

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'value',
        ]}

    @property
    def value(self) -> float:

        return self._value / 1000

    @value.setter
    def value(self, value: float) -> None:

        self._value = int(value * 1000)

    @property
    def payload(self) -> bytes | bytearray:

        return self._value.to_bytes(8, 'big', signed=True)

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        eight_bytes = bytes(it)
        assert len(eight_bytes) == 8

        self._value = int.from_bytes(eight_bytes, 'big', signed=True)
