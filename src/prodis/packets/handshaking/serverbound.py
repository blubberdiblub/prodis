#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    ByteString as _ByteString,
    Iterator as _Iterator,
    Union as _Union,
)

from itertools import islice as _islice

from ..packet import NewMinecraftPacket as _NewMinecraftPacket
from ..metaclasses import (
    IDDispatcher as _IDDispatcher,
    IDVerifier as _IDVerifier,
)

from .. import byteutils as _byteutils
from .. import iterutils as _iterutils


class Packet(_NewMinecraftPacket, metaclass=_IDDispatcher):

    def __str__(self) -> str:

        try:
            args = self._fmt_args()

        except AttributeError:
            return super().__str__()

        return f'{self.__class__.__name__}({args})'


class _VerifiedPacket(Packet, metaclass=_IDVerifier):

    pass


class Handshake(_VerifiedPacket):

    ID = 0x0

    def __init__(
            self,
            address: str = 'localhost',
            port: int = 25565,
            next_state: int = None,
            protocol: int = 578,
    ) -> None:

        super().__init__()

        self.address = address
        self.port = port
        self.next_state = next_state
        self.protocol = protocol

    def _fmt_args(self) -> str:

        return ', '.join([
            f'address={self.address!r}',
            f'port={self.port!r}',
            f'next_state={self.next_state!r}',
            f'protocol={self.protocol!r}',
        ])

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        it = iter(it)

        self.protocol = _iterutils.consume_varint(it)
        self.address = _iterutils.consume_string(it)
        self.port = int.from_bytes(_islice(it, 2), 'big')
        self.next_state, = it

        assert self.protocol == 578
        assert self.address
        assert self.port > 0
        assert self.next_state in [1, 2]

    def render_payload(self) -> _ByteString:

        return b'%b%b%b%c' % (
            _byteutils.render_varint(self.protocol),
            _byteutils.render_string(self.address),
            self.port.to_bytes(2, 'big'),
            self.next_state,
        )


Packet.packet_types = {
    Handshake.ID: Handshake
}
