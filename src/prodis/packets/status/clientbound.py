#!/usr/bin/env python3

from __future__ import annotations

from collections.abc import (
    Iterator as _Iterator,
)

import json as _json

from ..packet import MinecraftPacketWithID as _MinecraftPacketWithID

from ...utils import byte as _byte
from ...utils import iter as _iter


class Packet(_MinecraftPacketWithID):

    pass


class Response(Packet):

    id = 0x0

    def __init__(
            self,
            name: str = "Minecraft Server",
            protocol: int = 757,
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

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'name',
            'protocol',
            'players_max',
            'players_online',
            'description',
            'favicon',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

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

        return _byte.render_varstr(json)

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)

        json = _iter.consume_varstr(it)
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
        assert self.protocol == 757
        assert self.players_max >= 0
        assert self.players_online >= 0
        assert isinstance(self.description, str)
        assert self.favicon is None


# noinspection DuplicatedCode
class Pong(Packet):

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
