#!/usr/bin/env python3

from __future__ import annotations

from collections.abc import (
    Iterator as _Iterator,
)

from itertools import islice as _islice
from uuid import UUID as _UUID

from ..packet import MinecraftPacketWithID as _MinecraftPacketWithID

from ...utils import byte as _byte
from ...utils import iter as _iter


class Packet(_MinecraftPacketWithID):

    pass


class EncryptionRequest(Packet):

    id = 0x1

    def __init__(
            self,
            server_id: str = '',
            public_key: bytes = None,
            verify_token: bytes = None,
    ) -> None:

        super().__init__()

        self.server_id = server_id
        self.public_key = public_key
        self.verify_token = verify_token

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'server_id',
            'public_key',
            'verify_token',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return (
                _byte.render_varstr(self.server_id) +
                _byte.render_varint(len(self.public_key)) +
                self.public_key +
                _byte.render_varint(len(self.verify_token)) +
                self.verify_token
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.server_id = _iter.consume_varstr(it)
        self.public_key = _iter.consume_varbytes(it)
        self.verify_token = _iter.consume_varbytes(it)
        () = it


class LoginSuccess(Packet):

    id = 0x2

    def __init__(
            self,
            uuid: _UUID | str = None,
            username: str = None,
    ) -> None:

        if uuid and not isinstance(uuid, _UUID):
            uuid = _UUID(uuid)

        super().__init__()

        self.uuid = uuid
        self.username = username

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'uuid',
            'username',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return self.uuid.bytes + _byte.render_varstr(self.username)

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.uuid = _UUID(bytes=bytes(_islice(it, 16)))
        self.username = _iter.consume_varstr(it)
        () = it


class SetCompression(Packet):

    id = 0x3

    def __init__(self, threshold: int = -1) -> None:

        super().__init__()

        self.threshold = threshold

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'threshold',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return _byte.render_varint(self.threshold)

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.threshold = _iter.consume_varint(it)
        () = it
