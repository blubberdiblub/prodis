#!/usr/bin/env python3

from typing import Tuple as _Tuple

import asyncio as _asyncio
import sys as _sys

from .forevertask import ForeverTask as _ForeverTask
from .packetreader import PacketReader as _PacketReader
from .packetwriter import PacketWriter as _PacketWriter
from .packets import (
    protocol as _protocol,
    handshaking as _handshaking,
    status as _status,
    login as _login,
    play as _play,
)
from .packets.handshaking.serverbound import Handshake as _Handshake
from .packets.status.serverbound import (
    Request as _Request,
    Ping as _Ping,
)
from .packets.status.clientbound import (
    Response as _Response,
    Pong as _Pong,
)
from .packets.login.serverbound import (
    LoginStart as _LoginStart,
)
from .packets.login.clientbound import (
    LoginSuccess as _LoginSuccess,
)
from .packets.play.clientbound import (
    JoinGame as _JoinGame,
)


class ClientListener(_ForeverTask):

    async def _client_connected(
            self,
            reader: _asyncio.StreamReader,
            writer: _asyncio.StreamWriter,
    ) -> None:

        print("client connected", file=_sys.stderr, flush=True)

        protocol, next_state = await self._handshaking(reader)

        if next_state == 1:

            token = _protocol.set(protocol)
            await self._status(reader, writer)
            _protocol.reset(token)

            await self._expect_eof(reader, writer)

            if writer.can_write_eof():
                writer.write_eof()

            writer.close()
            await writer.wait_closed()
            return

        if next_state != 2:

            writer.close()
            raise NotImplementedError(f"unknown handshake state {next_state}")

        token = _protocol.set(protocol)
        await self._login(reader, writer)
        _protocol.reset(token)

        token = _protocol.set(protocol)
        await self._play(reader, writer)
        _protocol.reset(token)

        await self._expect_eof(reader, writer)

        if writer.can_write_eof():
            writer.write_eof()

        writer.close()
        await writer.wait_closed()
        return

    async def _expect_eof(self, reader: _asyncio.StreamReader, writer: _asyncio.StreamWriter) -> None:

        await writer.drain()

        if await reader.read(1):
            raise ValueError("unexpected data while waiting for EOF")

        assert reader.at_eof()

    async def _handshaking(
            self,
            reader: _asyncio.StreamReader,
    ) -> _Tuple[int, int]:

        packet_reader = _PacketReader(reader, _handshaking.ServerBound)
        async for packet in packet_reader:
            assert isinstance(packet, _Handshake)

            assert packet.protocol == 578
            assert packet.next_state in [1, 2]
            return packet.protocol, packet.next_state
        else:
            raise EOFError("client disconnected")

    async def _status(
            self,
            reader: _asyncio.StreamReader,
            writer: _asyncio.StreamWriter,
    ) -> None:

        packet_reader = _PacketReader(reader, _status.ServerBound)
        packet_writer = _PacketWriter(writer)

        async for packet in packet_reader:
            assert isinstance(packet, _Request)

            break
        else:
            raise EOFError("client disconnected")

        packet = _Response(description="Foobar")
        await packet_writer.write(packet)

        async for packet in packet_reader:
            assert isinstance(packet, _Ping)

            value = packet.value
            break
        else:
            raise EOFError("client disconnected")

        packet = _Pong(value=value)
        await packet_writer.write(packet)

    async def _login(
            self,
            reader: _asyncio.StreamReader,
            writer: _asyncio.StreamWriter,
    ) -> None:

        packet_reader = _PacketReader(reader, _login.ServerBound)
        packet_writer = _PacketWriter(writer)

        async for packet in packet_reader:
            assert isinstance(packet, _LoginStart)

            username = packet.name
            break
        else:
            raise EOFError("client disconnected")

        assert username.isalnum()
        uuid = '4465fcc3-d445-4ee2-bb00-7b39ce2d3cc7'

        packet = _LoginSuccess(uuid=uuid, username=username)
        await packet_writer.write(packet)

    async def _play(
            self,
            reader: _asyncio.StreamReader,
            writer: _asyncio.StreamWriter,
    ) -> None:

        packet_reader = _PacketReader(reader, _play.ServerBound)
        packet_writer = _PacketWriter(writer)

        packet = _JoinGame(entity_id=1, game_mode=0, dimension=0,
                           hashed_seed=0x0123456789abcdef)
        await packet_writer.write(packet)

        async for packet in packet_reader:

            break
        else:
            raise EOFError("client disconnected")

    async def _coroutine(self) -> None:

        loop = _asyncio.get_running_loop()

        server = await _asyncio.start_server(
            self._client_connected,
            host='localhost',
            port=25565,
            loop=loop,
        )

        if not server.sockets:
            raise ValueError("no sockets opened")

        return await server.serve_forever()

    def _get_future(self, loop) -> _asyncio.Task:

        return loop.create_task(self._coroutine())
