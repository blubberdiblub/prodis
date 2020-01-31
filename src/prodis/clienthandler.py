#!/usr/bin/env python3

from typing import (
    Any as _Any,
    Coroutine as _Coroutine,
    Callable as _Callable,
    Optional as _Optional,
    Tuple as _Tuple,
)

import asyncio as _asyncio
import sys as _sys

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


class ClientHandler:

    def __init__(
            self,
            reader: _asyncio.StreamReader,
            writer: _asyncio.StreamWriter,
            *,
            loop: _asyncio.AbstractEventLoop = None,
            task_name: str = None,
    ) -> None:

        if loop is None:
            loop = _asyncio.get_running_loop()

        self._reader = reader
        self._writer = writer
        self._exception = None
        self._result = None
        self._task = loop.create_task(self._handle(), name=task_name)

        def extract_result_and_clear_task(task) -> None:

            try:

                self._exception = task.exception()

            except _asyncio.CancelledError as exc:

                self._exception = exc

            else:

                if self._exception is None:
                    self._result = task.result()

            finally:

                self._task = None

        self._task.add_done_callback(extract_result_and_clear_task)

    def get_task(self) -> _Optional[_asyncio.Task]:

        return self._task

    def done(self) -> bool:

        return self._task is None

    def exception(self) -> _Optional[BaseException]:

        if self._task is not None:
            raise _asyncio.InvalidStateError("client handler still running")

        if self._exception is None:
            return None

        if isinstance(self._exception, _asyncio.CancelledError):
            raise self._exception

        return self._exception

    def result(self) -> _Any:

        if self._task is not None:
            raise _asyncio.InvalidStateError("client handler still running")

        exc = self.exception()
        if exc is not None:
            raise exc

        return self._result

    async def _handle(self) -> None:

        token = None

        try:

            protocol, next_state = await self._handshaking()

            token = _protocol.set(protocol)
            await self._state_machine(next_state)

        finally:

            if token is not None:
                _protocol.reset(token)

            if self._writer.can_write_eof():
                self._writer.write_eof()

            self._writer.close()
            await self._writer.wait_closed()

    async def _expect_eof(self) -> None:

        await self._writer.drain()

        if await self._reader.read(1):
            raise ValueError("unexpected data while waiting for EOF")

        assert self._reader.at_eof()

    async def _handshaking(self) -> _Tuple[int, _Coroutine]:

        packet_reader = _PacketReader(self._reader, _handshaking.ServerBound)
        async for packet in packet_reader:

            assert isinstance(packet, _Handshake)

            assert packet.protocol == 578
            protocol = packet.protocol
            next_state = {
                1: self._status,
                2: self._login,
            }[packet.next_state]
            break

        else:

            raise EOFError("client disconnected")

        return protocol, next_state()

    async def _state_machine(self, next_state: _Coroutine) -> None:

        while next_state is not None:
            next_state = await next_state

        await self._expect_eof()

    async def _status(self) -> _Optional[_Coroutine]:

        packet_reader = _PacketReader(self._reader, _status.ServerBound)
        packet_writer = _PacketWriter(self._writer)

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
        await self._expect_eof()

        return None

    async def _login(self) -> _Optional[_Coroutine]:

        packet_reader = _PacketReader(self._reader, _login.ServerBound)
        packet_writer = _PacketWriter(self._writer)

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

        return self._play()

    async def _play(self) -> _Optional[_Coroutine]:

        packet_reader = _PacketReader(self._reader, _play.ServerBound)
        packet_writer = _PacketWriter(self._writer)

        packet = _JoinGame(entity_id=1, game_mode=0, dimension=0,
                           hashed_seed=0x0123456789abcdef)
        await packet_writer.write(packet)

        async for packet in packet_reader:

            break
        else:
            raise EOFError("client disconnected")

        return None
