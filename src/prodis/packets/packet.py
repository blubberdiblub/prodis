#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    Type as _Type,
)

from collections.abc import (
    Generator as _Generator,
    Iterable as _Iterable,
    Iterator as _Iterator,
)

from zlib import (
    compress as _compress,
    decompress as _decompress,
)

from ..utils import fmt as _fmt
from ..utils import byte as _byte
from ..utils import iter as _iter
from ..utils import parse as _parse

from contextvars import ContextVar as _ContextVar

protocol = _ContextVar('protocol')
compression = _ContextVar('compression', default=-1)


class Packet:

    __raw_data: bytes | bytearray = None

    def __init__(self, payload: bytes | bytearray = None) -> None:

        super().__init__()

        if payload is not None:
            self.payload = payload

    def __setstate__(self, state: dict[str, object]) -> None:

        self.__init__(**state)

    def __getstate__(self) -> dict[str, object]:

        return ({'payload': self.payload} if type(self) is Packet
                else self.__dict__)

    def __repr__(self) -> str:

        args = (f"{k}={v!r}" for k, v in self.__getstate__().items())
        return f"{type(self).__qualname__}({', '.join(args)})"

    def __str__(self) -> str:

        try:
            payload = self.payload

        except AttributeError:
            return '<missing payload>'

        if payload is None:
            return '<missing payload>'

        return f"<{' '.join(f'{b:02x}' for b in payload)}>"

    @classmethod
    def _request_payload(cls) -> _Generator[
            int, bytes | bytearray, tuple[_Type[Packet], bytes | bytearray]]:

        raise NotImplementedError

    @classmethod
    def request(cls) -> _Generator[int, bytes | bytearray, Packet]:

        dispatched, payload = yield from cls._request_payload()
        packet = dispatched.__new__(dispatched)
        packet.payload = payload

        return packet

    @classmethod
    def _wrap(cls, data: bytes | bytearray) -> bytes | bytearray:

        return data

    def wrapped(self) -> bytes | bytearray:

        return self._wrap(self.payload)

    @property
    def payload(self) -> bytes | bytearray:

        return self.__raw_data

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterable[int]) -> None:

        self.__raw_data = bytes(it)


class MinecraftPacket(Packet):

    _payload: bytes | bytearray = None

    def __init__(self, payload: bytes | bytearray = None) -> None:

        super().__init__()

        if payload is not None:
            self.payload = payload

    def __getstate__(self) -> dict[str, object]:

        return ({'payload': self.payload} if type(self) is MinecraftPacket
                else self.__dict__)

    @classmethod
    def _request_payload(cls) -> _Generator[
            int, bytes | bytearray, tuple[_Type[Packet], bytes | bytearray]]:

        n = yield from _parse.request_varint()
        data = yield n

        if compression.get() >= 0:
            u, pos = _byte.parse_varint(data)
            data = data[pos:]

            if u:
                data = _decompress(data, bufsize=u)
                assert len(data) == u

        return cls, data

    # TODO: def unwrap(self, ...):

    @classmethod
    def _wrap(cls, data: bytes | bytearray) -> bytes | bytearray:

        if (threshold := compression.get()) >= 0:
            if (u := len(data)) >= threshold:
                data = _byte.render_varint(u) + _compress(data, level=1)
            else:
                data = b'\x00' + data

        return _byte.render_varint(len(data)) + data

    @property
    def payload(self) -> bytes | bytearray:

        return self._payload

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterable[int]) -> None:

        self._payload = bytes(it)


class _WithID(type):

    def __call__(
            cls: _Type[MinecraftPacketWithID],
            payload: bytes | bytearray = None,
            **kwargs
    ) -> MinecraftPacketWithID:

        if payload is None:
            packet = cls.__new__(cls, **kwargs)
            packet.__init__(**kwargs)
            return packet

        if kwargs:
            raise TypeError("cannot have both data and arguments")

        if cls.id is not None or not hasattr(cls, 'packet_types'):
            packet = cls.__new__(cls)
            packet.payload = payload
            return packet

        id_, start = _byte.parse_varint(payload)

        if id_ not in cls.packet_types:
            packet = cls.__new__(cls)
            packet.payload = payload
            return packet

        dispatched = cls.packet_types[id_]

        packet = dispatched.__new__(dispatched)
        packet.payload = payload[start:]
        return packet


class MinecraftPacketWithID(MinecraftPacket, metaclass=_WithID):

    id: int = None
    packet_types: dict[int, _Type[MinecraftPacketWithID]]

    @classmethod
    def __init_subclass__(cls, **kwargs) -> None:

        super().__init_subclass__(**kwargs)

        cls.packet_types = {}

        if cls.id is None:
            return

        base = cls
        while hasattr(base, 'packet_types'):
            assert cls.id not in base.packet_types
            base.packet_types[cls.id] = cls
            base, = base.__bases__

    def __getstate__(self) -> dict[str, object]:

        return ({'payload': self.payload} if type(self).id is None
                else self.__dict__)

    def __str__(self) -> str:

        cls = type(self)
        if cls.id is None:
            return super().__str__()

        args = (f"{k}={_fmt.abbr_str(v)}"
                for k, v in self.__getstate__().items())
        return f"{cls.__name__}({', '.join(args)})"

    @classmethod
    def _request_payload(cls) -> _Generator[
            int, bytes | bytearray, tuple[_Type[Packet], bytes | bytearray]]:

        _, payload = yield from super()._request_payload()

        id_, start = _byte.parse_varint(payload)

        try:
            dispatched = cls.packet_types[id_]

        except KeyError:
            if cls.id is not None:
                raise ValueError(f"unknown packet id {id_:#x}")

            dispatched = cls

        else:
            payload = payload[start:]

        return dispatched, payload

    @classmethod
    def _wrap(cls, data: bytes | bytearray) -> bytes | bytearray:

        if cls.id is not None:
            data = _byte.render_varint(cls.id) + data

        return super()._wrap(data)

    @property
    def payload(self) -> bytes | bytearray:

        if type(self).id is not None:
            return self._payload

        if self.id is None and self._payload is None:
            return None

        return _byte.render_varint(self.id) + self._payload

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterable[int]) -> None:

        if type(self).id is not None:
            self._payload = bytes(it)
            return

        it = iter(it)
        self.id = _iter.consume_varint(it)
        self._payload = bytes(it)
