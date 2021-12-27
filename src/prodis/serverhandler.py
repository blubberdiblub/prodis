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
    compression as _compression,
    handshaking as _handshaking,
    status as _status,
    login as _login,
    play as _play,
)

from .logger import Logger as _Logger
_log = _Logger(__name__)


class ServerHandler:

    _stream: _trio.abc.HalfCloseableStream
    _send_channel: _trio.abc.SendChannel
    _recv_channel: _trio.abc.ReceiveChannel

    def __init__(self, stream: _trio.abc.HalfCloseableStream,
                 send_channel: _trio.abc.SendChannel,
                 recv_channel: _trio.abc.ReceiveChannel) -> None:

        self._stream = stream
        self._send_channel = send_channel
        self._recv_channel = recv_channel

    async def run(self) -> None:

        async with self._stream, self._send_channel, self._recv_channel:

            protocol, next_state = await self._handshaking()

            with _let(_protocol, protocol):
                await self._state_machine(next_state)

    async def _expect_eof(self) -> None:

        await self._stream.wait_send_all_might_not_block()

        if await self._stream.receive_some(1):
            raise ValueError("unexpected data while waiting for EOF")

    async def _state_machine(self, next_state: _Awaitable) -> None:

        while next_state is not None:
            next_state = await next_state

        await self._expect_eof()

    async def _handshaking(self) -> tuple[int, _Coroutine]:

        packet_writer = _PacketWriter(self._stream)

        packet = await self._recv_channel.receive()
        assert isinstance(packet, _handshaking.serverbound.Handshake)
        assert packet.protocol == 757

        protocol = packet.protocol
        next_state = {
            1: self._status,
            2: self._login,
        }[packet.next_state]

        await packet_writer.write(packet)

        return protocol, next_state()

    async def _status(self) -> _Coroutine | None:

        packet_reader = _PacketReader(self._stream, _status.ClientBound)
        packet_writer = _PacketWriter(self._stream)

        packet = await self._recv_channel.receive()
        assert isinstance(packet, _status.serverbound.Request)
        await packet_writer.write(packet)

        async for packet in packet_reader:
            assert isinstance(packet, _status.clientbound.Response)
            await self._send_channel.send(packet)
            break

        else:
            raise EOFError("server disconnected")

        packet = await self._recv_channel.receive()
        assert isinstance(packet, _status.serverbound.Ping)
        await packet_writer.write(packet)

        async for packet in packet_reader:
            assert isinstance(packet, _status.clientbound.Pong)
            await self._send_channel.send(packet)
            break

        else:
            raise EOFError("server disconnected")

        await self._expect_eof()  # FIXME: redundant (see _state_machine)

        return None

    async def _login(self) -> _Coroutine | None:

        packet_reader = _PacketReader(self._stream, _login.ClientBound)
        packet_writer = _PacketWriter(self._stream)

        packet = await self._recv_channel.receive()
        assert isinstance(packet, _login.serverbound.LoginStart)
        await packet_writer.write(packet)

        async for packet in packet_reader:
            # if isinstance(packet, _login.clientbound.EncryptionRequest):
            #     _log.debug('|< {packet}', packet=packet)
            #     continue

            if isinstance(packet, _login.clientbound.SetCompression):
                _compression.set(packet.threshold)
                continue

            assert isinstance(packet, _login.clientbound.LoginSuccess)
            await self._send_channel.send(packet)
            break

        else:
            raise EOFError("server disconnected")

        return self._play()

    async def _play(self) -> _Coroutine | None:

        packet_reader = _PacketReader(self._stream, _play.ClientBound)
        packet_writer = _PacketWriter(self._stream)

        async for packet in packet_reader:
            assert isinstance(packet, _play.clientbound.JoinGame)
            await self._send_channel.send(packet)
            break

        else:
            raise EOFError("server disconnected")

        packet = await self._recv_channel.receive()
        assert isinstance(packet, _play.serverbound.ClientSettings)
        await packet_writer.write(packet)

        async with _trio.open_nursery() as nursery:
            nursery.start_soon(self._upstream, packet_writer)
            nursery.start_soon(self._downstream, packet_reader)

        return None

    async def _upstream(self, packet_writer: _PacketWriter) -> None:

        async for packet in self._recv_channel:
            await packet_writer.write(packet)

    async def _downstream(self, packet_reader: _PacketReader) -> None:

        async for packet in packet_reader:
            await self._send_channel.send(packet)
