#!/usr/bin/env python3

from __future__ import annotations

import asyncio as _asyncio

from .packets import Packet as _Packet

from .logger import Logger as _Logger
_log = _Logger(__name__)


class PacketWriter:

    def __init__(self, stream_writer: _asyncio.StreamWriter) -> None:

        self._stream_writer = stream_writer

    async def write(self, packet: _Packet, drain=True) -> None:

        _log.debug("-> %(packet)s", packet=packet)

        for data in packet.produce_raw():
            self._stream_writer.write(data)

        if drain:
            await self._stream_writer.drain()
