#!/usr/bin/env python3

from __future__ import annotations

from collections.abc import (
    Awaitable as _Awaitable,
    Coroutine as _Coroutine,
)

import trio as _trio

from .packetreader import PacketReader as _PacketReader
from .packetwriter import PacketWriter as _PacketWriter
from .utils.context import let as _let

from .packets import (
    protocol as _protocol,
    handshaking as _handshaking,
    status as _status,
    login as _login,
    play as _play,
)

from .logger import Logger as _Logger
_log = _Logger(__name__)


class ServerPinger:

    _stream: _trio.abc.HalfCloseableStream

    def __init__(self, stream: _trio.abc.HalfCloseableStream) -> None:

        self._stream = stream

    async def run(self) -> None:

        try:

            with _let(_protocol, 757):

                first_state = self._handshaking()
                await self._state_machine(first_state)

        finally:

            await self._stream.send_eof()
            await self._stream.aclose()

    async def _state_machine(self, next_state: _Awaitable) -> None:

        while next_state is not None:
            next_state = await next_state

        await self._expect_eof()

    async def _expect_eof(self) -> None:

        await self._stream.wait_send_all_might_not_block()

        if await self._stream.receive_some(1):
            raise ValueError("unexpected data while waiting for EOF")

    async def _handshaking(self) -> _Coroutine | None:

        packet_writer = _PacketWriter(self._stream)
        packet = _handshaking.serverbound.Handshake(next_state=1, protocol=-1)
        await packet_writer.write(packet)

        return self._status()

    async def _status(self) -> _Coroutine | None:

        packet_writer = _PacketWriter(self._stream)
        packet_reader = _PacketReader(self._stream, _status.ClientBound)

        packet = _status.serverbound.Request()
        await packet_writer.write(packet)

        async for packet in packet_reader:
            assert isinstance(packet, _status.clientbound.Response)

            self.response = packet
            break

        else:
            raise EOFError("server disconnected")

        packet = _status.serverbound.Ping(value=_trio.current_time())
        await packet_writer.write(packet)

        async for packet in packet_reader:
            assert isinstance(packet, _status.clientbound.Pong)

            self.roundtrip_time = _trio.current_time() - packet.value
            break

        else:
            raise EOFError("server disconnected")

        return None
