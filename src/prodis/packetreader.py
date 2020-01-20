#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    Type as _Type,
)

import trio as _trio

from .packets import Packet as _Packet

from .logger import Logger as _Logger
_log = _Logger(__name__)


class PacketReader:

    _receive_stream: _trio.abc.ReceiveStream
    _packet_type: _Type[_Packet]

    def __init__(
            self,
            receive_stream: _trio.abc.ReceiveStream,
            packet_type: _Type[_Packet],
    ) -> None:

        self._receive_stream = receive_stream
        self._packet_type = packet_type

    def __aiter__(self) -> PacketReader:

        return self

    async def __anext__(self) -> _Packet:

        requester = self._packet_type.request()
        data = None

        while True:
            try:
                num_bytes = requester.send(data)

            except StopIteration as exc:
                return exc.value

            data = await self._receive_stream.receive_some(num_bytes)
            if not data:
                raise StopAsyncIteration

            while len(data) < num_bytes:
                more_data = await self._receive_stream.receive_some(
                    num_bytes - len(data)
                )
                if not more_data:
                    raise StopAsyncIteration

                data += more_data
