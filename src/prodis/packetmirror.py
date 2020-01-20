#!/usr/bin/env python3

from __future__ import annotations

import trio as _trio

from .logger import Logger as _Logger
_log = _Logger(__name__)


class PacketMirror:

    _client_send_channel: _trio.abc.SendChannel
    _client_recv_channel: _trio.abc.ReceiveChannel
    _server_send_channel: _trio.abc.SendChannel
    _server_recv_channel: _trio.abc.ReceiveChannel
    _mirror_send_channel: _trio.abc.SendChannel

    def __init__(
            self,
            client_send_channel: _trio.abc.SendChannel,
            client_recv_channel: _trio.abc.ReceiveChannel,
            server_send_channel: _trio.abc.SendChannel,
            server_recv_channel: _trio.abc.ReceiveChannel,
            mirror_send_channel: _trio.abc.SendChannel,
    ) -> None:

        self._client_send_channel = client_send_channel
        self._client_recv_channel = client_recv_channel
        self._server_send_channel = server_send_channel
        self._server_recv_channel = server_recv_channel
        self._mirror_send_channel = mirror_send_channel

    async def run(self) -> None:

        async with _trio.open_nursery() as nursery:
            async with self._mirror_send_channel as mirror_channel:

                nursery.start_soon(self._mirror,
                                   self._server_recv_channel,
                                   self._client_send_channel,
                                   mirror_channel.clone(), False)

                nursery.start_soon(self._mirror,
                                   self._client_recv_channel,
                                   self._server_send_channel,
                                   mirror_channel.clone(), True)

    @staticmethod
    async def _mirror(recv_channel, send_channel,
                      mirror_channel, direction) -> None:

        async with recv_channel, send_channel, mirror_channel:
            async for packet in recv_channel:
                await send_channel.send(packet)
                await mirror_channel.send((direction, packet))
