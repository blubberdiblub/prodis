#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    ByteString as _ByteString,
    Iterator as _Iterator,
    Union as _Union,
)

import json as _json

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


class Response(_VerifiedPacket):

    ID = 0x0

    def __init__(
            self,
            name: str = "Minecraft Server",
            protocol: int = 578,
            players_max: int = 20,
            players_online: int = 0,
            description: str = "",
            favicon=None,
    ) -> None:

        super().__init__()

        self.name = name
        self.protocol = protocol
        self.players_max = players_max
        self.players_online = players_online
        self.description = description
        self.favicon = None

    def _fmt_args(self) -> str:

        return ', '.join([
            f'name={self.name!r}',
            f'protocol={self.protocol!r}',
            f'players_max={self.players_max!r}',
            f'players_online={self.players_online!r}',
            f'description={self.description!r}',
            f'favicon={self.favicon!r}',
        ])

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        it = iter(it)

        json = _iterutils.consume_string(it)
        () = it

        data = _json.loads(json)

        version = data['version']
        self.name = version['name']
        self.protocol = version['protocol']

        players = data['players']
        self.players_max = players['max']
        self.players_online = players['online']

        self.description = data['description']['text']
        self.favicon = None

        assert isinstance(self.name, str)
        assert self.protocol == 578
        assert self.players_max >= 0
        assert self.players_online >= 0
        assert isinstance(self.description, str)
        assert self.favicon is None

    def render_payload(self) -> _ByteString:

        json = _json.dumps({
            'version': {
                'name': self.name,
                'protocol': self.protocol,
            },
            'players': {
                'max': self.players_max,
                'online': self.players_online,
                'sample': [],
            },
            'description': {
                'text': self.description,
            },
        }, separators=(',', ':'))

        return _byteutils.render_string(json)


class Pong(_VerifiedPacket):

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
    Response.ID: Response,
    Pong.ID: Pong,
}
