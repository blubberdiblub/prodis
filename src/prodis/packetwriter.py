#!/usr/bin/env python3

from __future__ import annotations

import trio as _trio

from .packets import Packet as _Packet

from .logger import Logger as _Logger
_log = _Logger(__name__)


class PacketWriter:

    def __init__(self, send_stream: _trio.abc.SendStream) -> None:

        self._send_stream = send_stream

    async def write(self, packet: _Packet, drain=True) -> None:

        await self._send_stream.send_all(packet.wrapped())

        if drain:
            await self._send_stream.wait_send_all_might_not_block()
