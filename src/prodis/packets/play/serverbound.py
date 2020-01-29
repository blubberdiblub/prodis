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


Packet.packet_types = {
#    LoginStart.ID: LoginStart,
}
