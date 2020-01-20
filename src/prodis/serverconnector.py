#!/usr/bin/env python3

from __future__ import annotations

import trio as _trio

from .serverpinger import ServerPinger as _ServerPinger

from .logger import Logger as _Logger
_log = _Logger(__name__)


class ServerConnector:

    host: str
    port: int
    retry_delay: float
    reconnect_delay: float

    def __init__(self, host: str = 'localhost', port: int = 14454,
                 retry_delay: float = 3, reconnect_delay: float = 1) -> None:

        self.host = host
        self.port = port
        self.retry_delay = retry_delay
        self.reconnect_delay = reconnect_delay

    async def run(self) -> None:

        while True:

            try:
                stream = await _trio.open_tcp_stream(
                    host=self.host,
                    port=self.port,
                )

            except ConnectionError:

                await _trio.sleep(self.retry_delay)
                continue

            except OSError as exc:

                # FIXME: handle more gracefully
                raise RuntimeError("probably failed to connect or something")

            server_pinger = _ServerPinger(stream)
            await server_pinger.run()
            await _trio.sleep(self.reconnect_delay)
