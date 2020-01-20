#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    ByteString as _ByteString,
    Iterator as _Iterator,
    Union as _Union,
)

from ..packet import NewMinecraftPacket as _NewMinecraftPacket
from ..metaclasses import (
    IDDispatcher as _IDDispatcher,
    IDVerifier as _IDVerifier,
)


class Packet(_NewMinecraftPacket, metaclass=_IDDispatcher):

    def __str__(self) -> str:

        try:
            args = self._fmt_args()

        except AttributeError:
            return super().__str__()

        return f'{self.__class__.__name__}({args})'


class _VerifiedPacket(Packet, metaclass=_IDVerifier):

    pass


class Request(_VerifiedPacket):

    ID = 0x0

    def __init__(self) -> None:

        super().__init__()

    def _fmt_args(self) -> str:

        return ''

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        () = it

    def render_payload(self) -> _ByteString:

        return b''


class Ping(_VerifiedPacket):

    ID = 0x1

    def __init__(self, value: int = 0) -> None:

        super().__init__()

        self.value = value

    def _fmt_args(self) -> str:

        return f'value={self.value!r}'

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        eight_bytes = bytes(it)
        assert len(eight_bytes) == 8

        self.value = int.from_bytes(eight_bytes, 'big', signed=True)

    def render_payload(self) -> _ByteString:

        return self.value.to_bytes(8, 'big', signed=True)


Packet.packet_types = {
    Request.ID: Request,
    Ping.ID: Ping,
}
