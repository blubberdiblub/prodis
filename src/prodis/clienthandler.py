#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    Any as _Any,
    Coroutine as _Coroutine,
    Callable as _Callable,
    Optional as _Optional,
    Tuple as _Tuple,
)

import asyncio as _asyncio
import contextvars as _contextvars

from .packetreader import PacketReader as _PacketReader
from .packetwriter import PacketWriter as _PacketWriter
from .packets import (
    protocol as _protocol,
    handshaking as _handshaking,
    status as _status,
    login as _login,
    play as _play,
)

from .logger import Logger as _Logger
_log = _Logger(__name__)


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

        self._done_callbacks = []
        self._exception = None
        self._result = None
        self._task = loop.create_task(self._handle(), name=task_name)

        def extract_result_and_clear_task(task) -> None:

            try:

                self._exception = task.exception()

            except _asyncio.CancelledError as exc:

                self._exception = exc
                _log.debug("ClientHandler was cancelled")

            else:

                if self._exception is None:

                    self._result = task.result()

                else:

                    _log.exception(
                        "exception occurred in ClientHandler: {type}: {text}",
                        type=self._exception.__class__.__name__,
                        text=str(self._exception),
                        exc_info=self._exception, stack_info=False,
                    )

            finally:

                self._task = None

            for callback, context in self._done_callbacks:
                context.run(callback, self)

        self._task.add_done_callback(extract_result_and_clear_task)

    def add_done_callback(self, callback: _Callable[[ClientHandler], None], *,
                          context: _contextvars.Context = None) -> None:

        if self._task is None:

            _asyncio.get_running_loop().call_soon(callback, context=context)
            return

        self._done_callbacks.append(
            (
                callback,
                context if context is not None else _contextvars.copy_context(),
            )
        )

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

            assert isinstance(packet, _handshaking.serverbound.Handshake)

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
            assert isinstance(packet, _status.serverbound.Request)

            break
        else:
            raise EOFError("client disconnected")

        packet = _status.clientbound.Response(description="Foobar")
        await packet_writer.write(packet)

        async for packet in packet_reader:
            assert isinstance(packet, _status.serverbound.Ping)

            value = packet.value
            break
        else:
            raise EOFError("client disconnected")

        packet = _status.clientbound.Pong(value=value)
        await packet_writer.write(packet)
        await self._expect_eof()

        return None

    async def _login(self) -> _Optional[_Coroutine]:

        packet_reader = _PacketReader(self._reader, _login.ServerBound)
        packet_writer = _PacketWriter(self._writer)

        async for packet in packet_reader:
            assert isinstance(packet, _login.serverbound.LoginStart)

            username = packet.name
            break
        else:
            raise EOFError("client disconnected")

        assert username.isalnum()
        uuid = '4465fcc3-d445-4ee2-bb00-7b39ce2d3cc7'

        packet = _login.clientbound.LoginSuccess(uuid=uuid, username=username)
        await packet_writer.write(packet)

        return self._play()

    async def _play(self) -> _Optional[_Coroutine]:

        packet_reader = _PacketReader(self._reader, _play.ServerBound)
        packet_writer = _PacketWriter(self._writer)

        packet = _play.clientbound.JoinGame(
            entity_id=1,
            game_mode=0,
            dimension=0,
            hashed_seed=0x0123456789abcdef,
        )
        await packet_writer.write(packet)

        async for packet in packet_reader:
            assert isinstance(packet, _play.serverbound.ClientSettings)

            break
        else:
            raise EOFError("client disconnected")

        async for packet in packet_reader:
            pass
        else:
            raise EOFError("client disconnected")

        return None
