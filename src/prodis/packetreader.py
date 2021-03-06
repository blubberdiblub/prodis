#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    Type as _Type,
    Union as _Union,
)

import asyncio as _asyncio

from .packets import Packet as _Packet

from .logger import Logger as _Logger
_log = _Logger(__name__)


class PacketReader:

    def __init__(
            self,
            stream_reader: _asyncio.StreamReader,
            packet_type: _Type[_Packet] = None,
    ) -> None:

        self._stream_reader = stream_reader
        self._packet_type = packet_type

    def __aiter__(self) -> PacketReader:

        return self

    async def __anext__(self) -> _Union[_Packet, bytes]:

        try:
            packet_length = await self._packet_length()
            if packet_length <= 0:
                raise ValueError("illegal packet length")

            data = await self._stream_reader.readexactly(packet_length)

        except _asyncio.IncompleteReadError as e:
            if self._stream_reader.at_eof():
                raise StopAsyncIteration from e

            raise

        if self._packet_type is None:

            # noinspection PyUnreachableCode
            if __debug__:
                _log.debug("<- [{hex}]", hex=data.hex(sep=' '))

            return data

        try:

            packet = self._packet_type(data)

        except Exception:

            _log.debug("<- [{hex}]", hex=data.hex(sep=' '))
            raise

        # noinspection PyUnreachableCode
        if __debug__:
            _log.debug("<- {packet}", packet=packet)

        return packet

    async def _packet_length(self) -> int:

        octet, = await self._stream_reader.readexactly(1)
        if not octet & 0x80:
            return octet

        value = octet & 0x7f
        for shift in range(7, 32, 7):
            octet, = await self._stream_reader.readexactly(1)
            if not octet & 0x80:
                value |= octet << shift
                break
            value |= (octet & 0x7f) << shift
        else:
            raise ValueError("varint too long")

        if shift == 28:
            if octet > 0xf:
                raise ValueError("varint out of range")
            if octet & 0x8:
                return value | -0x80000000

        return value
