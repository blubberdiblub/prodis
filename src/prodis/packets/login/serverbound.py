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


class LoginStart(_VerifiedPacket):

    ID = 0x0

    def __init__(self, name: str = None) -> None:

        super().__init__()

        self.name = name

    def _fmt_args(self) -> str:

        return f'name={self.name!r}'

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        it = iter(it)
        self.name = _iterutils.consume_string(it)
        () = it

    def render_payload(self) -> _ByteString:

        return _byteutils.render_string(self.name)


Packet.packet_types = {
    LoginStart.ID: LoginStart,
}
