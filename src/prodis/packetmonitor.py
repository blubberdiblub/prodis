#!/usr/bin/env python3

from __future__ import annotations

import trio as _trio

from .packets.play.clientbound import ChunkData as _ChunkData

from .logger import Logger as _Logger
_log = _Logger(__name__)


class PacketMonitor:

    _recv_channel: _trio.abc.ReceiveChannel

    def __init__(self, recv_channel: _trio.abc.ReceiveChannel) -> None:

        self._recv_channel = recv_channel

    async def run(self) -> None:

        filter_chunkdata = False

        async with self._recv_channel:
            async for direction, packet in self._recv_channel:
                if not direction and isinstance(packet, _ChunkData):
                    if filter_chunkdata:
                        continue
                    filter_chunkdata = True

                _log.debug("{symbol} {packet}",
                           symbol='->' if direction else '<-', packet=packet)
