#!/usr/bin/env python3

from __future__ import annotations

from collections.abc import (
    Iterator as _Iterator,
)

from ..packet import MinecraftPacketWithID as _MinecraftPacketWithID

from ...utils import byte as _byte
from ...utils import iter as _iter


class Packet(_MinecraftPacketWithID):

    pass


class LoginStart(Packet):

    id = 0x0

    def __init__(self, name: str = None) -> None:

        super().__init__()

        self.name = name

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'name',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return _byte.render_varstr(self.name)

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.name = _iter.consume_varstr(it)
        () = it
