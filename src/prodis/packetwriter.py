#!/usr/bin/env python3

from __future__ import annotations

import asyncio as _asyncio

from .packets import Packet as _Packet


class PacketWriter:

    def __init__(self, stream_writer: _asyncio.StreamWriter) -> None:

        self._stream_writer = stream_writer

    async def write(self, packet: _Packet, drain=True) -> None:

        print("->", packet, flush=True)

        for data in packet.produce_raw():
            self._stream_writer.write(data)

        if drain:
            await self._stream_writer.drain()
