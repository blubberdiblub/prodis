#!/usr/bin/env python3

from __future__ import annotations

from collections.abc import (
    Iterator as _Iterator,
)

from itertools import islice as _islice

from ..packet import MinecraftPacketWithID as _MinecraftPacketWithID

from ...utils import byte as _byte
from ...utils import iter as _iter


class Packet(_MinecraftPacketWithID):

    pass


class Handshake(Packet):

    id = 0x0

    def __init__(
            self,
            address: str = 'localhost',
            port: int = 25565,
            next_state: int = None,
            protocol: int = 757,
    ) -> None:

        super().__init__()

        self.address = address
        self.port = port
        self.next_state = next_state
        self.protocol = protocol

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'address',
            'port',
            'next_state',
            'protocol',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b%b%c' % (
            _byte.render_varint(self.protocol),
            _byte.render_varstr(self.address),
            self.port.to_bytes(2, 'big'),
            self.next_state,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)

        self.protocol = _iter.consume_varint(it)
        self.address = _iter.consume_varstr(it)
        self.port = int.from_bytes(_islice(it, 2), 'big')
        self.next_state, = it

        assert self.protocol == 757
        assert self.address
        assert self.port > 0
        assert self.next_state in [1, 2]
