#!/usr/bin/env python3

from typing import (
    ByteString as _ByteString,
    Iterator as _Iterator,
    Optional as _Optional,
    Union as _Union,
)

import asyncio as _asyncio

from itertools import islice as _islice

from . import byteutils as _byteutils
from . import iterutils as _iterutils

from contextvars import ContextVar as _ContextVar

protocol = _ContextVar('protocol')


class Packet:

    def __init__(self, raw_data: _Optional[_ByteString]) -> None:

        self.__data = raw_data

    def _fmt_args(self) -> str:

        return f'raw_data={self.__data!r}'

    def __repr__(self) -> str:

        try:
            args = self._fmt_args()

        except AttributeError:
            return super().__repr__()

        return f'{self.__class__.__qualname__}({args})'

    def __str__(self) -> str:

        try:
            dump = ' '.join(f"{b:02x}" for b in self.__data)

        except (AttributeError, TypeError):
            return super().__str__()

        return f'<{dump}>'

    # def parse_data(self) -> None:
    #
    #     raise NotImplementedError

    # def render_data(self) -> None:
    #
    #     raise NotImplementedError

    def produce_raw(self) -> _Iterator[_ByteString]:

        yield self.__data


class NewMinecraftPacket(Packet):

    ID = None

    def __init__(
            self,
            payload: _ByteString = None,
    ) -> None:

        super().__init__(None)

        self.payload = payload

    def _fmt_args(self) -> str:

        return '' if self.payload is None else f'payload={self.payload!r}'

    # def consume_raw(self, it: _Iterator[int]) -> None:
    #
    #     packet_length = _iterutils.consume_varint(it)
    #     if packet_length <= 0:
    #         raise ValueError("illegal packet length")
    #
    #     it = _islice(it, packet_length)
    #     packet_id = _iterutils.consume_varint(it)
    #
    #     if packet_id != self.ID:
    #
    #         raise ValueError("packet ID mismatch")
    #
    #     self.consume_payload(it)

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        self.payload = bytes(it)

    def render_payload(self) -> _ByteString:

        return self.payload

    def produce_raw(self) -> _Iterator[_ByteString]:

        payload = self.render_payload()

        packet_id = _byteutils.render_varint(self.ID)

        yield _byteutils.render_varint(len(packet_id) + len(payload))
        yield packet_id
        yield payload
