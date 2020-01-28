#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    ByteString as _ByteString,
    Iterator as _Iterator,
    Union as _Union,
)

from uuid import UUID as _UUID

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


class LoginSuccess(_VerifiedPacket):

    ID = 0x2

    def __init__(
            self,
            uuid: _Union[_UUID, str] = None,
            username: str = None,
    ) -> None:

        if uuid is not None and not isinstance(uuid, _UUID):
            uuid = _UUID(uuid)

        super().__init__()

        self.uuid = uuid
        self.username = username

    def _fmt_args(self) -> str:

        return ', '.join([
            f'uuid={self.uuid!r}',
            f'username={self.username!r}',
        ])

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        it = iter(it)
        self.uuid = _UUID(_iterutils.consume_string(it))
        self.username = _iterutils.consume_string(it)
        () = it

    def render_payload(self) -> _ByteString:

        return (_byteutils.render_string(str(self.uuid)) +
                _byteutils.render_string(self.username))


Packet.packet_types = {
    LoginSuccess.ID: LoginSuccess,
}
