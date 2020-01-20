#!/usr/bin/env python3

from __future__ import annotations

import trio as _trio

from .clienthandler import ClientHandler as _ClientHandler
from .serverhandler import ServerHandler as _ServerHandler
from .packetmirror import PacketMirror as _PacketMirror
from .packetmonitor import PacketMonitor as _PacketMonitor

from .logger import Logger as _Logger
_log = _Logger(__name__)


class ClientListener:

    listen_host: str | None
    listen_port: int
    connect_host: str
    connect_port: int

    _cancel_scope: _trio.CancelScope | None = None

    def __init__(
            self,
            listen_host: str = 'localhost',
            listen_port: int = 25565,
            connect_host: str = 'localhost',
            connect_port: int = 14454,
    ) -> None:

        self.listen_host = listen_host
        self.listen_port = listen_port
        self.connect_host = connect_host
        self.connect_port = connect_port

    async def _client_connected(
            self,
            client_stream: _trio.abc.HalfCloseableStream,
    ) -> None:

        _log.notice("client connected")

        # TODO: configure host/port properly instead of hard-coding them
        server_stream = await _trio.open_tcp_stream(
                host=self.connect_host,
                port=self.connect_port,
        )

        _log.notice("connected to server")

        up_send1, up_recv1 = _trio.open_memory_channel(0)
        dn_send1, dn_recv1 = _trio.open_memory_channel(0)

        up_send2, up_recv2 = _trio.open_memory_channel(0)
        dn_send2, dn_recv2 = _trio.open_memory_channel(0)

        mon_send, mon_recv = _trio.open_memory_channel(100)

        client_handler = _ClientHandler(client_stream, up_send1, dn_recv1)
        server_handler = _ServerHandler(server_stream, dn_send2, up_recv2)
        packet_mirror = _PacketMirror(dn_send1, up_recv1, up_send2, dn_recv2,
                                      mon_send)
        packet_monitor = _PacketMonitor(mon_recv)

        async with _trio.open_nursery() as nursery:
            nursery.start_soon(client_handler.run)
            nursery.start_soon(server_handler.run)
            nursery.start_soon(packet_monitor.run)
            nursery.start_soon(packet_mirror.run)

    async def run(self) -> None:

        assert self._cancel_scope is None

        async with _trio.open_nursery() as nursery:

            self._cancel_scope = nursery.cancel_scope

            try:
                await _trio.serve_tcp(
                    self._client_connected,
                    port=self.listen_port,
                    host=self.listen_host,
                    handler_nursery=nursery,
                )

            finally:
                self._cancel_scope = None
